"""
RAG Agent Service

Core agent implementation with OpenAI Agents SDK for retrieval-augmented generation.
Can be used by both CLI and API layers.
"""

import uuid
import logging
from typing import Optional, Dict, Any
from openai import OpenAI

from config import AppConfig, load_config
from agent_types import AgentResponse, AgentError, ConversationState
from tools import search


logger = logging.getLogger(__name__)


# Default system prompt for the agent
DEFAULT_SYSTEM_PROMPT = """You are a helpful AI assistant specializing in robotics, ROS 2, simulation, Isaac Sim, and Vision-Language-Action (VLA) models for humanoid robots.

Your knowledge comes from a curated documentation knowledge base covering four main topics:
1. ROS 2 (Robot Operating System 2)
2. Robotics Simulation fundamentals
3. Isaac Sim (NVIDIA's robotics simulation platform)
4. VLA (Vision-Language-Action models)

IMPORTANT INSTRUCTIONS:

1. **Always use the search tool** when answering questions about these topics. Do not rely on your training data alone.

2. **Ground all responses in retrieved content**. When providing information:
   - Cite the source URLs from the search results
   - Quote or paraphrase directly from the retrieved text
   - If multiple sources are relevant, synthesize information from all of them

3. **Be transparent about knowledge limitations**:
   - If search returns no results or an error, explicitly tell the user: "I don't have information about that in the documentation knowledge base."
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


class RAGAgent:
    """
    Intelligent conversational agent with retrieval-augmented generation.

    Uses OpenAI Chat Completions API with function calling to decide when to
    invoke retrieval tool for grounding responses in documentation.
    """

    def __init__(self, config: Optional[AppConfig] = None):
        """
        Initialize RAG agent with configuration.

        Args:
            config: Application configuration (defaults to load from environment)
        """
        if config is None:
            config = load_config()

        self.config = config

        # Initialize OpenAI client with optional base_url for OpenRouter
        client_kwargs = {"api_key": config.openai_api_key}
        if config.openai_base_url:
            client_kwargs["base_url"] = config.openai_base_url

        self.client = OpenAI(**client_kwargs)
        self.state = self._create_state()

        if config.verbose:
            logger.info(f"RAGAgent initialized with model: {config.agent_model}")
            if config.openai_base_url:
                logger.info(f"Using custom base URL: {config.openai_base_url}")
            logger.info(f"Session ID: {self.state.session_id}")

    def _create_state(self) -> ConversationState:
        """Create new conversation state."""
        return ConversationState(session_id=str(uuid.uuid4()))

    async def chat(
        self,
        user_message: str,
        session_id: Optional[str] = None,
        top_k: Optional[int] = None,
        model: Optional[str] = None
    ) -> AgentResponse:
        """
        Send a message to the agent and get a grounded response.

        Args:
            user_message: User's natural language query
            session_id: Session identifier (if continuing conversation)
            top_k: Number of chunks to retrieve (default from config)
            model: Override default model (if needed)

        Returns:
            AgentResponse with content, sources, and metadata

        Raises:
            AgentError: On configuration or processing error
        """
        import time

        if not user_message or not user_message.strip():
            raise AgentError("user_message must not be empty")

        start_time = time.time()

        # Use config defaults if not specified
        top_k = top_k if top_k is not None else self.config.top_k_retrieval
        model = model if model is not None else self.config.agent_model
        system_prompt = self.config.agent_system_prompt or DEFAULT_SYSTEM_PROMPT

        # Track retrieval status
        retrieval_performed = False
        retrieved_sources = []
        error_message = None

        try:
            # Step 1: Perform retrieval
            from agent_types import SearchResponse, RetrievalError

            try:
                search_response: SearchResponse = await search(user_message, self.config, top_k)
                retrieval_performed = True
                retrieved_sources = [chunk.url for chunk in search_response.results]

                # Prepare context from retrieved chunks
                context = self._format_retrieval_context(search_response)

            except RetrievalError as e:
                context = f"Error: Failed to retrieve information. Details: {str(e)}"
                logger.error(f"Retrieval failed: {e}")

            # Step 2: Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            if context:
                messages.append({
                    "role": "system",
                    "content": f"Context from documentation:\n\n{context}"
                })

            # Step 3: Call OpenAI API
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=self.config.agent_temperature,
                max_tokens=self.config.agent_max_tokens
            )

            assistant_content = response.choices[0].message.content or ""

            # Update state
            self.state.turn_count += 1
            if retrieval_performed:
                self.state.retrieval_count += 1
            self.state.total_tokens += response.usage.total_tokens

            # Build response
            exec_time = time.time() - start_time

            return AgentResponse(
                content=assistant_content,
                sources=retrieved_sources,
                retrieval_performed=retrieval_performed,
                tokens_used=response.usage.total_tokens,
                execution_time_seconds=exec_time,
                turn_number=self.state.turn_count,
                session_id=self.state.session_id,
                error=error_message,
                model=model
            )

        except Exception as e:
            logger.error(f"Agent error: {e}")
            return AgentResponse(
                content="I encountered an error processing your request. Please try again.",
                sources=[],
                retrieval_performed=retrieval_performed,
                tokens_used=0,
                execution_time_seconds=time.time() - start_time,
                turn_number=self.state.turn_count,
                session_id=self.state.session_id,
                error=str(e),
                model=model
            )

    def _format_retrieval_context(self, search_response: SearchResponse) -> str:
        """
        Format retrieved chunks as context for the agent.

        Args:
            search_response: Search response with retrieved chunks

        Returns:
            Formatted context string
        """
        if not search_response.results:
            return "No relevant information found in the documentation knowledge base."

        context_parts = []
        for i, chunk in enumerate(search_response.results[:5], 1):
            source_info = f" [{chunk.title}]({chunk.url})" if chunk.title else f" [{chunk.url}]"
            context_parts.append(f"{i}. {source_info}\n{chunk.chunk_text[:300]}...")

        return "\n\n".join(context_parts)

    def reset_session(self) -> str:
        """
        Reset conversation history and start fresh.

        Returns:
            New session ID
        """
        old_session_id = self.state.session_id
        self.state = self._create_state()

        if self.config.verbose:
            logger.info(f"Session reset: {old_session_id} -> {self.state.session_id}")

        return self.state.session_id

    def get_state(self) -> ConversationState:
        """
        Get current conversation state.

        Returns:
            ConversationState with turn count, retrieval count, etc.
        """
        return self.state


def create_agent(config: Optional[AppConfig] = None) -> RAGAgent:
    """
    Factory function to create RAG agent instance.

    Args:
        config: Application configuration

    Returns:
        Initialized RAGAgent instance

    Raises:
        ConfigurationError: If configuration is invalid
    """
    return RAGAgent(config)
