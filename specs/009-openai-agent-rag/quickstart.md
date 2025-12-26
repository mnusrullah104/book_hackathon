# Quickstart: OpenAI Agent with RAG Retrieval

**Feature**: 009-openai-agent-rag
**Estimated Setup Time**: 10 minutes
**Prerequisites**: Python 3.9+, existing backend setup with Qdrant collection

## Overview

This guide walks you through setting up and testing the RAG-enabled conversational agent. By the end, you'll have a working agent that can query your documentation knowledge base and provide grounded responses.

---

## 1. Prerequisites Check

Ensure you have the following ready:

- ✅ Python 3.9 or higher installed
- ✅ Existing Qdrant collection `web_documents` with ingested documentation
- ✅ Cohere API key (for embeddings)
- ✅ Qdrant Cloud credentials (URL and API key)
- ✅ OpenAI API key (new requirement)

**Verify existing setup**:
```bash
cd backend
python check_qdrant.py
```

You should see confirmation that the `web_documents` collection exists and contains documents.

---

## 2. Install Dependencies

Add OpenAI SDK to your Python environment:

```bash
cd backend
pip install openai
```

**Verify installation**:
```bash
python -c "import openai; print(openai.__version__)"
```

Expected output: `1.x.x` (version 1.0 or higher)

---

## 3. Configure Environment Variables

Add your OpenAI API key to the `.env` file:

```bash
# Open .env in your editor
notepad .env  # Windows
nano .env     # Linux/Mac

# Add this line
OPENAI_API_KEY=sk-proj-...your-key-here...
```

**Verify all required credentials** are present in `.env`:
```bash
# Required keys:
COHERE_API_KEY=...
QDRANT_URL=...
QDRANT_API_KEY=...
OPENAI_API_KEY=...
```

---

## 4. Test Retrieval Functionality

Before using the agent, verify retrieval works:

```bash
python retrieve.py "What is ROS 2?"
```

**Expected output**:
```
[QUERY] What is ROS 2?
[RESULTS] 5 chunks
[TOP SCORE] 0.847
[AVG SCORE] 0.723
[TIME] 1.24s
```

If you see errors, troubleshoot:
- **Qdrant connection error**: Check `QDRANT_URL` and `QDRANT_API_KEY`
- **Cohere API error**: Check `COHERE_API_KEY` and rate limits
- **No results**: Verify collection has documents (`python check_qdrant.py`)

---

## 5. Run Your First Agent Query

Create `agent.py` (see implementation in `/sp.tasks` phase) and test:

```bash
python test_agent.py "Explain ROS 2 fundamentals"
```

**Expected output**:
```
[QUERY] Explain ROS 2 fundamentals
[RETRIEVING] Searching documentation...
[SOURCES] 5 chunks retrieved from 3 documents
[RESPONSE]
ROS 2 (Robot Operating System 2) is the next generation of ROS, designed with
improvements in performance, real-time capabilities, and security. Key features include:

1. **DDS Middleware**: Uses Data Distribution Service for improved communication
2. **Real-time Support**: Better deterministic behavior for robotics applications
3. **Security**: Built-in authentication and encryption
4. **Multi-platform**: Supports Linux, Windows, and macOS

**Sources:**
- [ROS 2 Basics](https://docs.example.com/module1/ros2-intro)
- [ROS 2 Architecture](https://docs.example.com/module1/ros2-arch)

[METADATA]
- Turn: 1
- Tokens: ~280
- Time: 3.4s
- Retrieval: Yes
```

---

## 6. Test Multi-Turn Conversation

Start an interactive session:

```bash
python test_agent.py --interactive
```

**Try this conversation flow**:
```
You: What is ROS 2?
Agent: [Retrieves and explains ROS 2]

You: How do I use it with Isaac Sim?
Agent: [Retrieves integration information, maintains context]

You: Show me a code example
Agent: [Provides grounded code examples from documentation]

You: Thanks!
Agent: You're welcome! Let me know if you have more questions.

You: exit
```

---

## 7. Run Test Suite

Validate agent behavior across diverse queries:

```bash
python test_agent.py --test-suite
```

**Test suite includes**:
1. ✅ Single-topic queries (ROS 2, Isaac Sim, VLA)
2. ✅ Cross-module queries (ROS 2 + Isaac Sim integration)
3. ✅ Follow-up questions (maintaining context)
4. ✅ Out-of-scope queries (weather, sports)
5. ✅ Vague queries (testing clarification)

**Expected results**:
- ✅ 10/10 queries processed successfully
- ✅ Retrieval performed for in-scope queries
- ✅ Source citations present in responses
- ✅ Graceful handling of out-of-scope queries

---

## 8. Common Issues and Solutions

### Issue: `openai.error.AuthenticationError`

**Cause**: Invalid or missing OpenAI API key

**Solution**:
```bash
# Verify API key in .env
cat .env | grep OPENAI_API_KEY

# Test key directly
python -c "import openai; openai.api_key='YOUR_KEY'; print(openai.Model.list())"
```

---

### Issue: `ConfigurationError: OPENAI_API_KEY not provided`

**Cause**: `.env` file not loaded or key not set

**Solution**:
```bash
# Check if .env exists
ls -la .env

# Verify python-dotenv is installed
pip install python-dotenv

# Test loading
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

---

### Issue: Agent doesn't cite sources

**Cause**: System prompt not enforcing citation policy

**Solution**: Verify the system prompt in `agent.py` includes source citation instructions (see `contracts/system-prompt.md`)

---

### Issue: Slow response times (>10s per query)

**Cause**: Model selection or network latency

**Solution**:
```bash
# Try faster model
python test_agent.py "Test query" --model gpt-3.5-turbo

# Check network latency to OpenAI
ping api.openai.com
```

---

### Issue: High API costs

**Cause**: Using gpt-4 with large context windows

**Solution**:
- Use `gpt-3.5-turbo` for development/testing (10x cheaper)
- Reduce `top_k` to 3 instead of 5 (fewer tokens in context)
- Truncate chunk text to 300 chars instead of 500

---

## 9. Next Steps

### Local Development
- ✅ Modify system prompt in `agent.py` to customize behavior
- ✅ Add custom test queries to `test_agent.py`
- ✅ Experiment with different models (`gpt-4`, `gpt-3.5-turbo-16k`)
- ✅ Adjust `top_k` and `score_threshold` for retrieval tuning

### Production Preparation
- 📋 Integrate agent into FastAPI (see `/sp.tasks` for implementation plan)
- 📋 Add authentication and user management
- 📋 Implement conversation persistence (database storage)
- 📋 Set up monitoring and logging (tokens, latency, errors)
- 📋 Add rate limiting and request queuing

### Advanced Features
- 📋 Implement streaming responses for real-time feedback
- 📋 Add feedback collection (thumbs up/down on responses)
- 📋 Multi-agent orchestration (routing queries to specialized agents)
- 📋 Custom retrieval filters (e.g., module-specific search)

---

## 10. Validation Checklist

Before proceeding to implementation (`/sp.tasks`), verify:

- ✅ Agent initializes without errors
- ✅ Single query returns grounded response with sources
- ✅ Multi-turn conversation maintains context
- ✅ Out-of-scope queries handled gracefully
- ✅ Retrieval errors don't crash agent
- ✅ Response times < 5 seconds on average
- ✅ Test suite passes with 90%+ success rate

---

## Resources

- **Specification**: [spec.md](./spec.md)
- **Implementation Plan**: [plan.md](./plan.md)
- **Data Model**: [data-model.md](./data-model.md)
- **API Contract**: [contracts/agent-api.md](./contracts/agent-api.md)
- **System Prompt**: [contracts/system-prompt.md](./contracts/system-prompt.md)
- **Retrieval Tool Schema**: [contracts/retrieval-tool-schema.json](./contracts/retrieval-tool-schema.json)

---

## Troubleshooting Contact

If you encounter issues not covered here:

1. Check the [existing backend README](../../backend/README.md) for ingestion troubleshooting
2. Verify Qdrant collection status: `python check_qdrant.py`
3. Test retrieval independently: `python retrieve.py "test query"`
4. Review logs in `backend/*.log` (if logging configured)
5. Consult OpenAI API documentation: https://platform.openai.com/docs

---

**Ready to implement?** Run `/sp.tasks` to generate the task breakdown for building `agent.py` and `test_agent.py`.
