# Observability in LangGraph & LangSmith

This guide explains the core concepts of observability in LangGraph applications using LangSmith, and how to effectively track, debug, and monitor your agentic workflows.

## 1. What is the use of Observability?

Observability in AI systems—especially non-deterministic, agentic systems built with LangGraph—allows you to see the "inner workings" of your application. When an agent runs, it might make multiple LLM calls, use various tools, and route through different nodes. Observability helps you:

*   **Debug:** See exactly which tool was called, what arguments were passed, what the exact LLM prompt was, and where an error occurred.
*   **Monitor:** Track token usage, compute costs, and latency across your entire application to ensure it's performant and cost-effective.
*   **Evaluate & Improve:** Record interactions to create datasets for evaluation or fine-tuning later.
*   **Understand State Transitions:** In LangGraph, it helps you visualize the graph execution path (which nodes were visited, how the state changed after each node).

## 2. How to use Observability in LangGraph

LangGraph has native, built-in integration with LangSmith. You don't need to change your Python code to start tracing. You only need to set a few environment variables.

### Environment Setup

Set these environment variables in your terminal or `.env` file before running your LangGraph code:

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY="ls__your_langsmith_api_key"
export LANGCHAIN_PROJECT="My_LangGraph_Project"
```

*   `LANGCHAIN_TRACING_V2=true`: Turns on the tracing engine.
*   `LANGCHAIN_API_KEY`: Your authentication key from smith.langchain.com.
*   `LANGCHAIN_PROJECT`: (Optional) Groups your traces into a specific project. If omitted, traces go to the "default" project.

Once these are set, any time you call `graph.invoke()`, the entire execution process is automatically logged to LangSmith.

## 3. What is a Trace in LangSmith?

A **Trace** represents the complete end-to-end execution of a single request or operation in your application.

Think of a trace as a **tree of operations** (often called a tree of "Runs" or "Spans"). 
*   The **root** of the tree is the initial call to your LangGraph (e.g., `graph.invoke(...)`).
*   The **branches and leaves** are the internal steps: nodes executing, LLMs generating text, tools fetching data, and retrievers querying databases.

By looking at a trace, you can expand and collapse these steps to see exactly what happened sequentially and hierarchically.

## 4. What Information is in a Trace?

When you open a trace in LangSmith, you will see a detailed breakdown of every step. For each step (Run), you get the following information:

1.  **Inputs and Outputs:** The exact data that went into a step and the data that came out. For an LLM, this shows the exact formatted prompt text and the generated response.
2.  **Metadata & Tags:** Custom information you can attach (like `user_id`, `session_id`, or application version).
3.  **Metrics:** Token usage (Prompt Tokens, Completion Tokens, Total Tokens) and Latency (Execution time).
4.  **Errors:** If a node or tool crashes, the stack trace and error message are attached directly to the run that failed.
5.  **State Changes (Specific to LangGraph):** You can see how your LangGraph `State` mutated after each node executed.

## 5. How to Observe Token Usage and Latency

When using LangSmith, token usage and latency are captured **automatically** for supported LLM integrations (like `ChatOpenAI`, `ChatAnthropic`, etc.).

*   **Latency:** LangSmith automatically timestamps the start and end of every operation. The UI visually displays the duration of each step, allowing you to easily spot bottlenecks (e.g., a slow API tool or a slow LLM response).
*   **Token Usage:** Modern LLM APIs return token usage statistics in their API responses. LangChain/LangGraph automatically extracts this data from the `response_metadata` and sends it to LangSmith.
    *   In the LangSmith UI, you will see a "Metrics" tab or section for LLM runs displaying Prompt Tokens, Completion Tokens, Total Tokens, and Estimated Cost.
    *   These metrics roll up to the top of the trace, so you can see the total cost and latency for the entire LangGraph execution at a glance.
