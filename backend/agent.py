
"""
RAG Agent with OpenAI Function Calling

Intelligent conversational agent that uses retrieval-augmented generation (RAG)
to ground responses in documentation from the knowledge base.
"""

import os
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import openai

# Import existing retrieval functionality
from retrieve import search, ConfigurationError, QdrantConnectionError, CohereAPIError


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# DATA CLASSES (Phase 2: T004-T008)
# =============================================================================

@dataclass
class AgentConfig:
    """Configuration for RAG agent initialization."""

    openai_api_key: str
    """OpenAI API key for agent model access (or OpenRouter API key)."""

    model: str = "mistralai/devstral-2-2512:free"
    """Model identifier. Supports OpenRouter models (e.g., 'mistralai/devstral-2-2512:free') or OpenAI models."""

    base_url: Optional[str] = None
    """Custom API base URL. Set to 'https://openrouter.ai/api/v1' for OpenRouter."""

    system_prompt: str = ""
    """Instructions defining agent behavior and retrieval grounding."""

    temperature: float = 0.7
    """Sampling temperature (0.0-2.0). Lower = more deterministic."""

    max_tokens: int = 1000
    """Maximum tokens in agent response."""

    top_k_retrieval: int = 5
    """Default number of chunks to retrieve per query."""

    retrieval_score_threshold: float = 0.3
    """Minimum similarity score for retrieved chunks (0.0-1.0)."""

    cohere_api_key: Optional[str] = None
    """Cohere API key for embeddings (defaults to env var)."""

    qdrant_url: Optional[str] = None
    """Qdrant instance URL (defaults to env var)."""

    qdrant_api_key: Optional[str] = None
    """Qdrant API key (defaults to env var)."""

    collection_name: str = "web_documents"
    """Target Qdrant collection."""

    verbose: bool = False
    """Enable detailed logging."""

    max_context_tokens: int = 12000
    """Maximum tokens for conversation context (system + messages)."""


@dataclass
class ConversationMessage:
    """A single message in the conversation history."""

    role: str
    """Message role: 'system', 'user', 'assistant', or 'function'."""

    content: Optional[str] = None
    """Message text content (None for function call requests)."""

    name: Optional[str] = None
    """Function name (only for role='function')."""

    function_call: Optional[dict] = None
    """Function call details (only for assistant function invocations)."""

    def to_dict(self) -> dict:
        """Convert to OpenAI API format."""
        msg = {"role": self.role}
        if self.content is not None:
            msg["content"] = self.content
        if self.name is not None:
            msg["name"] = self.name
        if self.function_call is not None:
            msg["function_call"] = self.function_call
        return msg

    @classmethod
    def from_dict(cls, data: dict) -> "ConversationMessage":
        """Create from OpenAI API response."""
        return cls(
            role=data["role"],
            content=data.get("content"),
            name=data.get("name"),
            function_call=data.get("function_call")
        )


@dataclass
class ConversationSession:
    """Maintains state for a multi-turn conversation."""

    session_id: str
    """Unique session identifier (UUID4)."""

    messages: List[ConversationMessage] = field(default_factory=list)
    """Ordered conversation history."""

    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    """ISO 8601 timestamp of session creation."""

    turn_count: int = 0
    """Number of user turns (queries) in this session."""

    retrieval_count: int = 0
    """Number of retrieval tool invocations."""

    total_tokens_used: int = 0
    """Approximate token usage across all turns."""

    def add_message(self, message: ConversationMessage):
        """Append message to history."""
        self.messages.append(message)
        if message.role == "user":
            self.turn_count += 1
        elif message.role == "function" and message.name == "search_docs":
            self.retrieval_count += 1

    def get_message_history(self) -> List[dict]:
        """Get conversation history in OpenAI API format."""
        return [msg.to_dict() for msg in self.messages]

    def get_last_assistant_message(self) -> Optional[str]:
        """Get most recent assistant response text."""
        for msg in reversed(self.messages):
            if msg.role == "assistant" and msg.content:
                return msg.content
        return None

    def _estimate_tokens(self, text: Optional[str]) -> int:
        """
        Estimate token count from text (rough approximation: ~4 chars per token).

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count (0 for None/empty)
        """
        if not text:
            return 0
        # Rough approximation: ~4 characters per token
        return len(text) // 4

    def prune_for_token_limit(self, max_tokens: int, system_prompt_length: int = 0):
        """
        Prune conversation history to stay within token limit.

        Keeps system message and most recent messages, removing oldest user/assistant
        pairs when approaching token budget.

        Args:
            max_tokens: Maximum tokens allowed for context
            system_prompt_length: Estimated tokens in system prompt
        """
        if not self.messages:
            return

        # Calculate estimated current token count
        estimated_tokens = system_prompt_length
        for msg in self.messages:
            if msg.content:
                estimated_tokens += self._estimate_tokens(msg.content)
            if msg.function_call:
                # Function calls add ~50-100 tokens
                estimated_tokens += 75

        # If under limit, no pruning needed
        if estimated_tokens < max_tokens * 0.8:  # Leave 20% buffer
            return

        if self.verbose:
            logger.info(f"Token limit reached (estimated: {estimated_tokens}, limit: {max_tokens}), pruning conversation")

        # Keep system message, remove oldest user/assistant pairs
        # Start from index 1 (after system message)
        new_messages = [self.messages[0]]  # Always keep system message
        removed_turns = 0

        # Add messages from end, removing pairs from beginning until under limit
        tokens_after_system = 0
        i = len(self.messages) - 1
        while i > 0:
            msg = self.messages[i]
            msg_tokens = self._estimate_tokens(msg.content) if msg.content else 0
            if msg.function_call:
                msg_tokens += 75

            # Check if adding this message keeps us under limit
            if tokens_after_system + msg_tokens > max_tokens * 0.7:  # More aggressive pruning
                break

            # Prepend to build list in reverse order
            new_messages.insert(1, msg)
            tokens_after_system += msg_tokens

            # Track removed turns (user messages)
            if msg.role == "user":
                removed_turns += 1

            i -= 1

        self.messages = new_messages

        if self.verbose:
            logger.info(f"Pruned {removed_turns} turns, kept {len(self.messages)} messages, estimated tokens: ~{system_prompt_length + tokens_after_system}")


@dataclass
class RetrievalToolResponse:
    """Structured retrieval results formatted for agent consumption."""

    results: List[dict] = field(default_factory=list)
    """
    List of retrieved chunks, each containing:
    - text: str (truncated to 500 chars)
    - url: str (source document URL)
    - title: str (document title)
    - score: float (similarity score, 3 decimal places)
    """

    total: int = 0
    """Number of results returned."""

    query: str = ""
    """Original search query."""

    error: Optional[str] = None
    """Error type if retrieval failed."""

    message: Optional[str] = None
    """Human-readable error message."""

    execution_time_seconds: float = 0.0
    """Retrieval operation duration."""

    def to_json(self) -> str:
        """Serialize to JSON string for function message content."""
        return json.dumps({
            "results": self.results,
            "total": self.total,
            "query": self.query,
            "error": self.error,
            "message": self.message,
            "execution_time": round(self.execution_time_seconds, 2)
        }, indent=2)

    def is_error(self) -> bool:
        """Check if retrieval encountered an error."""
        return self.error is not None


@dataclass
class AgentResponse:
    """Agent response to user query with metadata."""

    content: str
    """Agent's text response."""

    session_id: str
    """Associated conversation session."""

    turn_number: int
    """Turn index in conversation (1-indexed)."""

    retrieval_performed: bool
    """Whether retrieval tool was invoked."""

    retrieved_sources: List[str] = field(default_factory=list)
    """URLs of documents used for grounding."""

    tokens_used: int = 0
    """Tokens consumed in this turn (approximate)."""

    execution_time_seconds: float = 0.0
    """Total response generation time."""

    error: Optional[str] = None
    """Error message if response generation failed."""


# =============================================================================
# SYSTEM PROMPT (Phase 2: T011)
# =============================================================================

DEFAULT_SYSTEM_PROMPT = """You are a helpful AI assistant specializing in robotics, ROS 2, simulation, Isaac Sim, and Vision-Language-Action (VLA) models for humanoid robots.

Your knowledge comes from a curated documentation knowledge base covering four main topics:
1. ROS 2 (Robot Operating System 2)
2. Robotics Simulation fundamentals
3. Isaac Sim (NVIDIA's robotics simulation platform)
4. VLA (Vision-Language-Action models)

IMPORTANT INSTRUCTIONS:

1. **Always use the search_docs tool** when answering questions about these topics. Do not rely on your training data alone.

2. **Ground all responses in retrieved content**. When providing information:
   - Cite the source URLs from the search results
   - Quote or paraphrase directly from the retrieved text
   - If multiple sources are relevant, synthesize information from all of them

3. **Be transparent about knowledge limitations**:
   - If search_docs returns no results or an error, explicitly tell the user: "I don't have information about that in the documentation knowledge base."
   - Do not make up facts or provide information not present in the retrieved content
   - If the query is outside the scope of the four topic areas, acknowledge this limitation

4. **Maintain conversational context**:
   - Reference previous exchanges when relevant
   - Ask clarifying questions if the user's query is ambiguous
   - Provide follow-up suggestions related to the current topic

5. **Format responses clearly**:
   - Use markdown for code blocks, lists, and emphasis
   - Structure long responses with headings and bullet points
   - Always include source citations at the end in this format:

   **Sources:**
   - [Document Title](URL)
   - [Document Title](URL)

6. **Handle errors gracefully**:
   - If retrieval fails due to a connection error, inform the user: "I'm having trouble accessing the documentation right now. Please try again."
   - Suggest rephrasing if a query is too vague to retrieve useful results

Your goal is to help AI engineers learn about and implement robotics systems using accurate, source-grounded information."""


# =============================================================================
# RETRIEVAL TOOL (Phase 2: T009)
# =============================================================================

async def retrieval_tool(
    query: str,
    top_k: int = 5,
    score_threshold: float = 0.3,
    cohere_api_key: Optional[str] = None,
    qdrant_url: Optional[str] = None,
    qdrant_api_key: Optional[str] = None,
    collection_name: str = "web_documents"
) -> RetrievalToolResponse:
    """
    Wrapper for retrieve.search() that returns OpenAI-compatible JSON.

    Args:
        query: Search query text
        top_k: Number of chunks to retrieve (1-10)
        score_threshold: Minimum similarity score (0.0-1.0)
        cohere_api_key: Cohere API key (defaults to env var)
        qdrant_url: Qdrant URL (defaults to env var)
        qdrant_api_key: Qdrant API key (defaults to env var)
        collection_name: Target collection name

    Returns:
        RetrievalToolResponse with results or error information
    """
    start_time = time.time()

    try:
        # Call existing retrieval function
        result = await search(
            query,
            top_k=top_k,
            score_threshold=score_threshold,
            cohere_api_key=cohere_api_key,
            qdrant_url=qdrant_url,
            qdrant_api_key=qdrant_api_key,
            collection_name=collection_name,
            verbose=False
        )

        # Check if no results found
        if result.total_results == 0:
            return RetrievalToolResponse(
                results=[],
                total=0,
                query=query,
                error="no_results",
                message="The knowledge base does not contain information about this query",
                execution_time_seconds=time.time() - start_time
            )

        # Format results for agent
        formatted_results = []
        for chunk in result.chunks:
            formatted_results.append({
                "text": chunk.chunk_text[:500] + ("..." if len(chunk.chunk_text) > 500 else ""),
                "url": chunk.url,
                "title": chunk.title or "Untitled",
                "score": round(chunk.similarity_score, 3)
            })

        return RetrievalToolResponse(
            results=formatted_results,
            total=result.total_results,
            query=query,
            execution_time_seconds=time.time() - start_time
        )

    except (QdrantConnectionError, CohereAPIError) as e:
        logger.error(f"Retrieval failed: {e}")
        return RetrievalToolResponse(
            results=[],
            total=0,
            query=query,
            error="retrieval_unavailable",
            message="Unable to search documentation at this time",
            execution_time_seconds=time.time() - start_time
        )
    except Exception as e:
        logger.error(f"Unexpected retrieval error: {e}")
        return RetrievalToolResponse(
            results=[],
            total=0,
            query=query,
            error="unknown_error",
            message=f"Retrieval failed: {str(e)}",
            execution_time_seconds=time.time() - start_time
        )


# =============================================================================
# FUNCTION CALLING SCHEMA (Phase 2: T010)
# =============================================================================

# Use newer OpenAI tools format (functions is deprecated)
RETRIEVAL_FUNCTION_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_docs",
        "description": "Search the documentation knowledge base for relevant information using semantic similarity. Use this tool when the user asks questions about ROS 2, robotics simulation, Isaac Sim, VLA (Vision-Language-Action models), or humanoid robots. The tool returns relevant document sections with source URLs.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query. Should be a clear, specific question or topic to find relevant documentation. Examples: 'How to set up ROS 2 for humanoid robots?', 'Isaac Sim fundamentals', 'What is VLA?'"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of relevant document chunks to retrieve. Default is 5. Use higher values (up to 10) for broad topics, lower values (3) for specific questions.",
                    "minimum": 1,
                    "maximum": 10,
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
}


# =============================================================================
# RAG AGENT CLASS (Phase 3: User Story 1 - T014-T023)
# =============================================================================

class RAGAgent:
    """
    Intelligent conversational agent with retrieval-augmented generation.

    Uses OpenAI Chat Completions API with function calling to decide when to
    invoke retrieval tool for grounding responses in documentation.
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize RAG agent with configuration.

        Args:
            config: AgentConfig with API keys and parameters
        """
        self.config = config

        # Import OpenAI SDK here and configure for OpenRouter if base_url is provided
        import openai

        client_kwargs = {"api_key": config.openai_api_key}
        if config.base_url:
            client_kwargs["base_url"] = config.base_url

        self.client = openai.OpenAI(**client_kwargs)
        self.session = self._create_session()

        if config.verbose:
            logger.info(f"RAGAgent initialized with model: {config.model}")
            if config.base_url:
                logger.info(f"Using custom base URL: {config.base_url}")
            logger.info(f"Session ID: {self.session.session_id}")

    def _create_session(self) -> ConversationSession:
        """Create a new conversation session with system prompt."""
        session = ConversationSession(session_id=str(uuid.uuid4()))

        # Add system message
        system_message = ConversationMessage(
            role="system",
            content=self.config.system_prompt
        )
        session.add_message(system_message)

        return session

    async def _call_openai(
        self,
        messages: List[dict],
        tools: Optional[List[dict]] = None
    ) -> dict:
        """
        Call OpenAI Chat Completions API.

        Args:
            messages: Conversation history in OpenAI format
            tools: Optional tool definitions for tool calling

        Returns:
            OpenAI response dictionary

        Raises:
            openai.OpenAIError: API call failed
        """
        try:
            kwargs = {
                "model": self.config.model,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens
            }

            if tools:
                kwargs["tools"] = tools

            response = self.client.chat.completions.create(**kwargs)

            if self.config.verbose:
                logger.info(f"OpenAI API call successful, model: {response.model}")

            return response

        except openai.AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {e}")
            raise
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            raise
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected OpenAI error: {e}")
            raise

    async def chat(
        self,
        user_message: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None
    ) -> AgentResponse:
        """
        Send a message to the agent and get a response.

        Args:
            user_message: User's natural language query (non-empty string)
            top_k: Number of chunks to retrieve (1-10, default: from config)
            score_threshold: Minimum similarity score (0.0-1.0, default: from config)

        Returns:
            AgentResponse with content, metadata, and source citations

        Raises:
            ValueError: Empty or invalid user_message
            CohereAPIError: Embedding generation failed
            QdrantConnectionError: Retrieval search failed
            openai.OpenAIError: Agent API call failed
        """
        start_time = time.time()

        # Validate input
        if not user_message or not user_message.strip():
            raise ValueError("user_message must not be empty")

        # Use config defaults if not specified
        top_k = top_k if top_k is not None else self.config.top_k_retrieval
        score_threshold = score_threshold if score_threshold is not None else self.config.retrieval_score_threshold

        if self.config.verbose:
            logger.info(f"Processing query: '{user_message[:50]}...'")

        # Add user message to conversation
        user_msg = ConversationMessage(role="user", content=user_message)
        self.session.add_message(user_msg)

        # Prune conversation history if approaching token limit
        # Estimate system prompt tokens (~3 chars per token)
        system_prompt_tokens = self.session._estimate_tokens(self.config.system_prompt) // 3
        self.session.prune_for_token_limit(
            max_tokens=self.config.max_context_tokens,
            system_prompt_length=system_prompt_tokens
        )

        # Track retrieval status
        retrieval_performed = False
        retrieved_sources = []
        error_message = None

        try:
            # For OpenRouter free models, do retrieval manually (no tool calling support)
            # Always perform retrieval first
            try:
                retrieval_result = await retrieval_tool(
                    query=user_message,
                    top_k=top_k,
                    score_threshold=score_threshold,
                    cohere_api_key=self.config.cohere_api_key,
                    qdrant_url=self.config.qdrant_url,
                    qdrant_api_key=self.config.qdrant_api_key,
                    collection_name=self.config.collection_name
                )
                retrieval_performed = True

                # Extract source URLs
                if not retrieval_result.is_error():
                    retrieved_sources = [r["url"] for r in retrieval_result.results]

                # Prepare context for the agent
                if retrieval_result.is_error():
                    context = "Retrieval failed. Please inform the user."
                elif not retrieval_result.results:
                    context = "No relevant information found in the documentation knowledge base."
                else:
                    # Format retrieved chunks as context
                    context_parts = []
                    for i, chunk in enumerate(retrieval_result.results[:5], 1):
                        source_info = f" [{chunk.get('title', 'Untitled')}]({chunk.get('url', '')})" if chunk.get('title') else f" [{chunk.get('url', '')}]"
                        text = chunk.get('text', '')[:300]
                        context_parts.append(f"{i}. {source_info}\n{text}...")
                    context = "\n\n".join(context_parts)

                # Get messages and add context
                messages = self.session.get_message_history()
                # Add context as system message after existing system message
                context_message = {"role": "system", "content": f"Here is relevant information from the documentation:\n\n{context}\n\nUse this information to answer the user's question. If you don't find relevant information here, say so clearly."}
                # Insert after first system message
                messages.insert(1, context_message)

            except Exception as e:
                error_message = f"Retrieval error: {str(e)}"
                logger.error(error_message)

                # Get messages without context if retrieval failed
                messages = self.session.get_message_history()

            # Call OpenAI
            try:
                response = await self._call_openai(messages=messages)
            except Exception as e:
                error_message = f"OpenAI API error: {str(e)}"
                logger.error(error_message)

                return AgentResponse(
                    content="I encountered an error processing your request. Please try again.",
                    session_id=self.session.session_id,
                    turn_number=self.session.turn_count,
                    retrieval_performed=False,
                    error=error_message,
                    execution_time_seconds=time.time() - start_time
                )

            choice = response.choices[0]

            # Extract final assistant response
            assistant_content = choice.message.content or ""

            # Add assistant response to conversation (only the actual message, not context)
            assistant_msg = ConversationMessage(role="assistant", content=assistant_content)
            self.session.add_message(assistant_msg)

            # Estimate token usage
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
            self.session.total_tokens_used += tokens_used

            # Build response
            exec_time = time.time() - start_time

            return AgentResponse(
                content=assistant_content,
                session_id=self.session.session_id,
                turn_number=self.session.turn_count,
                retrieval_performed=retrieval_performed,
                retrieved_sources=retrieved_sources,
                tokens_used=tokens_used,
                execution_time_seconds=exec_time
            )

        except (QdrantConnectionError, CohereAPIError) as e:
            error_message = f"Retrieval error: {str(e)}"
            logger.error(error_message)

            return AgentResponse(
                content="I'm having trouble accessing the documentation right now. Please try again.",
                session_id=self.session.session_id,
                turn_number=self.session.turn_count,
                retrieval_performed=False,
                error=error_message,
                execution_time_seconds=time.time() - start_time
            )

        except openai.OpenAIError as e:
            error_message = f"OpenAI API error: {str(e)}"
            logger.error(error_message)

            return AgentResponse(
                content="I encountered an error processing your request. Please try again.",
                session_id=self.session.session_id,
                turn_number=self.session.turn_count,
                retrieval_performed=False,
                error=error_message,
                execution_time_seconds=time.time() - start_time
            )

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            logger.error(error_message)

            return AgentResponse(
                content="An unexpected error occurred. Please try again.",
                session_id=self.session.session_id,
                turn_number=self.session.turn_count,
                retrieval_performed=False,
                error=error_message,
                execution_time_seconds=time.time() - start_time
            )

    def start_new_session(self) -> str:
        """
        Reset conversation history and start a fresh session.

        Returns:
            New session ID (UUID4 string)
        """
        self.session = self._create_session()

        if self.config.verbose:
            logger.info(f"Started new session: {self.session.session_id}")

        return self.session.session_id

    def get_session(self) -> ConversationSession:
        """
        Retrieve current conversation session state.

        Returns:
            ConversationSession with messages, turn count, retrieval count
        """
        return self.session

    def get_message_history(self) -> List[dict]:
        """
        Get conversation history in OpenAI API format.

        Returns:
            List of message dictionaries
        """
        return self.session.get_message_history()


# =============================================================================
# INITIALIZATION FUNCTION (Phase 2: T012-T013)
# =============================================================================

def create_agent(
    openai_api_key: Optional[str] = None,
    model: str = "mistralai/devstral-2-2512:free",
    base_url: Optional[str] = None,
    cohere_api_key: Optional[str] = None,
    qdrant_url: Optional[str] = None,
    qdrant_api_key: Optional[str] = None,
    collection_name: str = "web_documents",
    verbose: bool = False
) -> "RAGAgent":
    """
    Initialize a new RAG agent instance.

    Args:
        openai_api_key: OpenAI or OpenRouter API key (defaults to OPENROUTER_API_KEY or OPENAI_API_KEY env var)
        model: Model identifier (default: "mistralai/devstral-2-2512:free" for OpenRouter)
        base_url: Custom API base URL (defaults to None, or "https://openrouter.ai/api/v1" for OpenRouter)
        cohere_api_key: Cohere API key for embeddings (defaults to env var)
        qdrant_url: Qdrant instance URL (defaults to env var)
        qdrant_api_key: Qdrant API key (defaults to env var)
        collection_name: Target Qdrant collection (default: "web_documents")
        verbose: Enable detailed logging (default: False)

    Returns:
        Initialized RAGAgent instance

    Raises:
        ConfigurationError: Missing required API credentials
        ValueError: Invalid model name or parameters
    """
    # Load environment variables
    load_dotenv()

    # Auto-detect OpenRouter: check for OPENROUTER_API_KEY or base_url pattern
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_key:
        openai_key = openai_api_key or openrouter_key
        base_url = base_url or "https://openrouter.ai/api/v1"
    else:
        openai_key = openai_api_key or os.getenv("OPENAI_API_KEY")

    if not openai_key:
        raise ConfigurationError(
            "No API key found. Set OPENROUTER_API_KEY or OPENAI_API_KEY environment variable, or pass as parameter."
        )

    # Log configuration
    if verbose:
        logger.info(f"Using model: {model}")
        if base_url:
            logger.info(f"Using custom base URL: {base_url}")

    # Create configuration
    config = AgentConfig(
        openai_api_key=openai_key,
        model=model,
        base_url=base_url,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        cohere_api_key=cohere_api_key,
        qdrant_url=qdrant_url,
        qdrant_api_key=qdrant_api_key,
        collection_name=collection_name,
        verbose=verbose
    )

    # Setup logging
    if verbose:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    # Create and return RAGAgent instance
    return RAGAgent(config)


# =============================================================================
# ENTRY POINT FOR TESTING
# =============================================================================

if __name__ == "__main__":
    print("agent.py - RAG Agent with OpenAI Function Calling")
    print("Phase 2 (Foundational) complete: Dataclasses, configuration, retrieval tool")
    print("Phase 3 (User Story 1) complete: RAGAgent class with chat(), retrieval, error handling")
    print("Use test_agent.py for CLI testing")
