# Tracing and Observability in LangSmith

One of the most critical use cases of LangSmith is **Tracing**. When building LLM-based capabilities, especially chains and agents, a single user request can fan out into multiple LLM calls, document retrievals, and external API tool calls. 

## What is Tracing in the Context of LLMs?

Tracing provides granular, step-by-step visibility into the execution tree of an LLM application. Instead of looking at raw text logs, LangSmith visualizes the exact flow of data.

### Key Capabilities of LangSmith Tracing

1. **Full Execution Trees:**
   - **Chains:** See the exact input and output of every step in a LangChain sequence.
   - **Agents:** View the agent's internal monologue (reasoning), which tools it decided to call, the exact arguments passed to the tools, and the raw tool output.
   - **Retrieval (RAG):** Monitor what queries were sent to the vector database, the exact documents returned, and how the LLM utilized those documents to form an answer.

2. **Debugging Failures in Real-Time:**
   - With **Agent Studio**, you can visualize agent tasks, set breakpoints, and debug step-by-step.
   - If an LLM output fails a parsing step (e.g., failed to output valid JSON), you can pinpoint exactly which prompt caused the error, tweak the prompt in the LangSmith UI Playground, and re-run the trace without changing your codebase.

3. **Performance Monitoring & Cost Tracking:**
   - Every trace logs token consumption (prompt vs. completion tokens) and execution latency.
   - LangSmith automatically calculates the cost of the run based on the model provider's pricing, allowing you to identify expensive or slow bottlenecks.

4. **Conversation History:**
   - For chat-based applications, traces maintain conversation threads. This is crucial for debugging multi-turn dialogues where context is lost or the agent "forgets" previous instructions.

## Using LangSmith with LangChain

When using LangChain or LangGraph, tracing is almost entirely automated. By simply setting environment variables:

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY="ls__..."
export LANGCHAIN_PROJECT="my-agent-project"
```

Every `invoke`, `stream`, or `batch` call made by your LangChain objects will automatically stream telemetry to your LangSmith dashboard, capturing all intermediate states without writing manual logging code.
