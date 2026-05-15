"""
Module 11: Observability, Tracing, and LangSmith Integration
=============================================================

Demonstrates how to enable global tracing, monitor token usage, 
and interrogate execution latency using LangSmith.
"""

import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import AnyMessage
import operator

# ============================================================================
# 1. ENABLING OBSERVABILITY (LANGSMITH CONFIGURATION)
# ============================================================================
# In production, these should be set in a .env file or system environment.
# Setting them here for educational demonstration.

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "LangGraph_Observability_Masterclass"

# Note: LANGCHAIN_API_KEY and OPENAI_API_KEY must be set in the environment
# for this code to execute successfully and send traces to LangSmith.


class ObservabilityState(TypedDict):
    """
    Schema tracking message arrays with cumulative add_messages reducer.
    """
    messages: Annotated[list[AnyMessage], operator.add]


# ============================================================================
# 2. DEFINING THE TRACED NODES
# ============================================================================

def processor_node(state: ObservabilityState) -> dict:
    """
    Simulates a computational node performing LLM-backed analysis.
    
    Every operation inside this function (the LLM call, tool calls) 
    will appear as children in the LangSmith trace tree.
    """
    print("  [Node Execution] Invoking LLM via LangChain Interface...")
    
    # LangSmith automatically intercepts this call to record:
    # 1. Prompt String
    # 2. Token Usage (Prompt + Completion)
    # 3. Latency (ms)
    # 4. Model Version
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    response = llm.invoke(state["messages"])
    
    return {"messages": [response]}


def run_observability_demo():
    """
    Compiles and invokes a traced LangGraph application.
    """
    print(f"\n{'='*75}\nMODULE 11: LangSmith Observability & Tracing Demo\n{'='*75}")
    
    builder = StateGraph(ObservabilityState)
    builder.add_node("agent", processor_node)
    builder.add_edge(START, "agent")
    builder.add_edge("agent", END)
    
    # Compilation Phase
    app = builder.compile()
    
    # Invocation Phase (The 'Root' of the Trace)
    print("\nTriggering Graph Invocation... Check LangSmith UI for Real-Time Trace.")
    
    initial_input = {
        "messages": [("user", "Explain why Supersteps are important in LangGraph in 2 sentences.")]
    }
    
    # Passing 'config' with tags allows for advanced filtering in LangSmith
    config = {
        "configurable": {"thread_id": "obs_demo_001"},
        "tags": ["demo", "educational"],
        "metadata": {"user_id": "admin_user_99"}
    }
    
    result = app.invoke(initial_input, config=config)
    
    print("\nFinal Output Received:")
    print(f"  {result['messages'][-1].content}")


if __name__ == "__main__":
    run_observability_demo()
