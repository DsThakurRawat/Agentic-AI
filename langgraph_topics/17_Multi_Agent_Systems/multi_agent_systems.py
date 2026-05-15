"""
Module 17: Multi-Agent Systems & Supervisor Orchestration
=========================================================

Demonstrates the Supervisor-Worker pattern where a central LLM node
delegates tasks to specialized worker agents.
"""

from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
import operator

# ============================================================================
# 1. STATE DEFINITION
# ============================================================================

class MultiAgentState(TypedDict):
    """
    Unified state schema for multi-agent collaboration.
    """
    messages: Annotated[list[BaseMessage], add_messages]
    next_agent: str  # Controlled by the Supervisor


# ============================================================================
# 2. WORKER NODES
# ============================================================================

def researcher_node(state: MultiAgentState) -> dict:
    """Specialized worker for data retrieval."""
    print("  [Worker: Researcher] Performing deep-dive research...")
    return {"messages": [("assistant", "Research: Found 3 key facts about LangGraph MAS.")]}


def coder_node(state: MultiAgentState) -> dict:
    """Specialized worker for technical implementation."""
    print("  [Worker: Coder] Writing technical implementation code...")
    return {"messages": [("assistant", "Code: Implemented supervisor routing logic.")]}


# ============================================================================
# 3. THE SUPERVISOR (ORCHESTRATOR)
# ============================================================================

def supervisor_node(state: MultiAgentState) -> dict:
    """
    The Project Manager. Decides which agent should work next.
    """
    print("  [Supervisor] Analyzing progress and assigning next task...")
    
    # Simulating LLM routing logic
    history = [m.content for m in state["messages"]]
    
    if any("Research" in h for h in history) and any("Code" in h for h in history):
        return {"next_agent": "FINISH"}
    elif any("Research" in h for h in history):
        return {"next_agent": "coder"}
    else:
        return {"next_agent": "researcher"}


# ============================================================================
# 4. BUILDING THE MULTI-AGENT GRAPH
# ============================================================================

def build_mas_graph():
    builder = StateGraph(MultiAgentState)
    
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("researcher", researcher_node)
    builder.add_node("coder", coder_node)
    
    builder.add_edge(START, "supervisor")
    
    # Dynamic routing based on the supervisor's 'next_agent' decision
    builder.add_conditional_edges(
        "supervisor",
        lambda state: state["next_agent"],
        {
            "researcher": "researcher",
            "coder": "coder",
            "FINISH": END
        }
    )
    
    # Workers always report back to the supervisor
    builder.add_edge("researcher", "supervisor")
    builder.add_edge("coder", "supervisor")
    
    return builder.compile()


if __name__ == "__main__":
    print(f"\n{'='*75}\nMODULE 17: Multi-Agent Supervisor-Worker Demo\n{'='*75}")
    mas_app = build_mas_graph()
    
    initial_input = {"messages": [HumanMessage(content="Help me build a LangGraph app.")], "next_agent": ""}
    result = mas_app.invoke(initial_input)
    
    print("\nFinal Orchestration Log:")
    for msg in result["messages"]:
        print(f"  {msg.content}")
