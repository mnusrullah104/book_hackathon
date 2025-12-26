# Research: OpenAI Agent with RAG Retrieval Integration

**Feature**: 009-openai-agent-rag
**Date**: 2025-12-25
**Phase**: 0 - Research & Discovery

## Research Questions

### 1. OpenAI Agents SDK Architecture and Function Calling

**Question**: How does the OpenAI Agents SDK support function calling and tool integration for RAG retrieval?

**Decision**: Use OpenAI's function calling feature with the Assistants API or Chat Completions API to implement retrieval tool

**Rationale**:
- OpenAI supports function calling in both Assistants API and Chat Completions API
- Function calling allows the agent to decide when to invoke the retrieval tool based on query context
- The agent can be configured with a JSON schema describing the retrieval tool's parameters and return format
- For this implementation, Chat Completions API with function calling is simpler and more aligned with the modular CLI-first approach

**Alternatives Considered**:
1. **Assistants API**: More complex with built-in state management, threading, and tool use. Overkill for CLI-based MVP but good for future web integration
2. **Chat Completions with function calling**: Direct control over conversation flow, simpler state management, better for testing and iteration
3. **LangChain Agents**: Additional abstraction layer, but adds dependency complexity when OpenAI SDK alone is sufficient

**Selected Approach**: Chat Completions API with function calling (openai.ChatCompletion.create with functions parameter)

### 2. Conversation History Management

**Question**: How should multi-turn conversation context be maintained and passed to the OpenAI agent?

**Decision**: Maintain conversation history as a list of message dictionaries following OpenAI's message format

**Rationale**:
- OpenAI Chat API expects messages in format: `[{"role": "system"|"user"|"assistant"|"function", "content": "...", "name": "..."}]`
- System message defines agent behavior and instructs grounding in retrieved content
- User and assistant messages maintain conversational context
- Function messages inject retrieval results back into the conversation
- Simple list structure allows easy persistence, inspection, and debugging

**Implementation Pattern**:
```python
conversation_history = [
    {"role": "system", "content": "You are a helpful assistant..."},
    {"role": "user", "content": "What is ROS 2?"},
    {"role": "assistant", "content": None, "function_call": {"name": "search_docs", "arguments": {...}}},
    {"role": "function", "name": "search_docs", "content": "[retrieved chunks]"},
    {"role": "assistant", "content": "ROS 2 is..."}
]
```

**Alternatives Considered**:
1. **Session-based storage (Redis/DB)**: Too complex for CLI MVP, appropriate for future web deployment
2. **File-based persistence**: Unnecessary for per-session testing, can be added later if needed
3. **In-memory list**: Simple, testable, sufficient for CLI usage

### 3. Retrieval Tool Integration Pattern

**Question**: How should the retrieval functionality from `retrieve.py` be exposed as a tool to the OpenAI agent?

**Decision**: Create a wrapper function that formats retrieval results into a structured JSON response compatible with OpenAI function calling

**Rationale**:
- Existing `retrieve.py` provides `search()` function returning `RetrievalResult` with structured chunks
- OpenAI function calling expects JSON-serializable return values
- Need to format retrieved chunks into a concise format that fits within token limits
- Include essential metadata: chunk text, URL, similarity score, title

**Implementation Approach**:
```python
async def retrieval_tool(query: str, top_k: int = 5) -> dict:
    """
    Wrapper for retrieve.search() that returns OpenAI-compatible JSON.

    Returns:
        {
            "results": [
                {
                    "text": "chunk content...",
                    "url": "https://...",
                    "title": "Document Title",
                    "score": 0.85
                },
                ...
            ],
            "total": 5,
            "query": "original query"
        }
    """
    result = await search(query, top_k=top_k, verbose=False)
    return {
        "results": [
            {
                "text": chunk.chunk_text[:500],  # Truncate for token limits
                "url": chunk.url,
                "title": chunk.title,
                "score": round(chunk.similarity_score, 3)
            }
            for chunk in result.chunks
        ],
        "total": result.total_results,
        "query": result.query
    }
```

**Alternatives Considered**:
1. **Pass full RetrievedChunk objects**: Not JSON-serializable, excessive metadata
2. **Concatenate all chunk text**: Loses source attribution and explainability
3. **Return only top result**: Insufficient context for complex queries

### 4. Error Handling and Graceful Degradation

**Question**: How should the agent handle cases where retrieval fails or returns no results?

**Decision**: Implement explicit error handling with graceful fallback responses

**Rationale**:
- Retrieval can fail due to: Qdrant connection errors, Cohere API errors, no results above threshold
- Agent should transparently communicate limitations rather than hallucinating
- System prompt should instruct agent to acknowledge when information is unavailable

**Implementation Strategy**:
```python
# In retrieval tool wrapper
try:
    result = await search(query, top_k=top_k, score_threshold=0.3)
    if result.total_results == 0:
        return {
            "error": "No relevant information found",
            "message": "The knowledge base does not contain information about this query"
        }
    return format_results(result)
except Exception as e:
    logger.error(f"Retrieval failed: {e}")
    return {
        "error": "Retrieval unavailable",
        "message": "Unable to search documentation at this time"
    }

# System prompt instruction
"If the retrieval tool returns an error or no results, inform the user that you don't have information on that topic rather than making up facts."
```

**Alternatives Considered**:
1. **Silent failure with hallucination**: Violates constitutional principle of transparency
2. **Raise exceptions to user**: Poor UX, breaks conversation flow
3. **Return empty results**: Agent might hallucinate instead of acknowledging gap

### 5. Token Budget and Context Window Management

**Question**: How should we manage token limits when injecting retrieved context into the conversation?

**Decision**: Truncate chunk text to 500 characters per chunk, limit to top 5 results by default, include token counting for monitoring

**Rationale**:
- OpenAI models have context window limits (e.g., gpt-4-turbo: 128k tokens, gpt-3.5-turbo: 16k tokens)
- Retrieved chunks can be lengthy (up to 512 tokens each as per ingestion config)
- Need to balance context richness with token budget
- 5 chunks × 500 chars ≈ 2500 chars ≈ 625 tokens (rough estimate)
- Leaves ample room for system prompt, conversation history, and response generation

**Implementation**:
```python
# Truncate chunks in retrieval tool
"text": chunk.chunk_text[:500] + ("..." if len(chunk.chunk_text) > 500 else "")

# Make top_k configurable
async def chat(user_message: str, conversation_history: list, top_k: int = 5):
    ...
```

**Alternatives Considered**:
1. **No truncation**: Risk exceeding context limits on long conversations
2. **Smaller top_k (e.g., 3)**: May miss relevant context for complex queries
3. **Larger top_k (e.g., 10)**: Increases token usage and cost unnecessarily
4. **Dynamic adjustment**: Too complex for MVP, can optimize later

### 6. Testing Strategy for CLI Interface

**Question**: What test queries and validation approach should be used for CLI-based testing?

**Decision**: Create a test suite with 10-15 queries spanning all 4 topic modules with expected behavior validation

**Rationale**:
- Need to validate retrieval accuracy across diverse topics
- Test multi-turn conversation flow with follow-up questions
- Verify graceful handling of out-of-scope and edge case queries
- Ensure source citation appears in responses

**Test Query Categories**:
1. **Single-topic queries** (Module 1-4 specific): "Explain ROS 2 basics", "How does Isaac Sim work?"
2. **Cross-module queries**: "How do I use ROS 2 with Isaac Sim?"
3. **Follow-up questions**: "What is VLA?" → "How do I train one?"
4. **Edge cases**: "What's the weather today?" (out of scope), "Tell me about humanoid robots" (broad/vague)
5. **No-result scenarios**: Queries about content definitely not in knowledge base

**Validation Approach**:
```python
# test_agent.py structure
test_queries = [
    {
        "query": "Explain ROS 2 fundamentals",
        "expected_module": "Module 1",
        "should_cite_sources": True,
        "should_retrieve": True
    },
    {
        "query": "What's the weather today?",
        "expected_module": None,
        "should_cite_sources": False,
        "should_retrieve": False
    }
]

for test in test_queries:
    response = await agent.chat(test["query"])
    validate_response(response, test)
```

**Alternatives Considered**:
1. **Manual ad-hoc testing**: Not reproducible, time-consuming
2. **Automated integration tests with assertions**: Good for CI/CD but overkill for initial validation
3. **Interactive REPL**: Useful for exploration but doesn't validate systematic coverage

## Research Summary

All key technical decisions have been resolved:

1. **Agent Architecture**: OpenAI Chat Completions API with function calling (not Assistants API)
2. **Conversation Management**: In-memory message list following OpenAI format
3. **Retrieval Integration**: JSON wrapper around existing `retrieve.search()` with truncation
4. **Error Handling**: Explicit error returns with agent instruction to acknowledge gaps
5. **Token Management**: 500-char truncation per chunk, top_k=5 default
6. **Testing**: Structured CLI test suite with 10-15 queries across topic modules

No blockers identified. Ready to proceed to Phase 1 (Design & Contracts).
