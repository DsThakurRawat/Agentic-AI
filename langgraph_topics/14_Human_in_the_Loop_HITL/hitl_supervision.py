"""
Module 14: Human-in-the-Loop (HITL) Supervision & Interruption
==============================================================

Demonstrates how to implement security checkpoints using interrupt()
and Command(resume=...) to manage high-risk agentic actions.
"""

from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages

# ============================================================================
# 1. STATE DEFINITION
# ============================================================================

class HITLState(TypedDict):
    """
    Schema tracking conversations requiring administrative approval.
    """
    messages: Annotated[list[BaseMessage], add_messages]
    action_pending: bool


# ============================================================================
# 2. NODES & TOOLS
# ============================================================================

def supervisor_node(state: HITLState) -> dict:
    """
    Evaluates intent and determines if a high-risk action is requested.
    """
    last_msg = state["messages"][-1].content
    print(f"  [Supervisor] Analyzing request: '{last_msg}'")
    
    # Logic to flag high-risk actions
    is_risky = "purchase" in last_msg.lower() or "delete" in last_msg.lower()
    return {"action_pending": is_risky}


def secure_action_node(state: HITLState) -> dict:
    """
    Performs the high-risk action ONLY after passing the interrupt barrier.
    """
    # ------------------------------------------------------------------------
    # THE DYNAMIC INTERRUPT
    # This pauses the graph and waits for the caller to provide a 'resume' value.
    # ------------------------------------------------------------------------
    print("  [Security Gateway] ACTION INTERRUPTED: Awaiting human approval...")
    
    # This payload is sent back to the user via result['__interrupt__']
    human_decision = interrupt("Confirm this high-risk transaction? (yes/no)")
    
    if human_decision.lower() == "yes":
        print("  [Security Gateway] APPROVED: Executing destructive action.")
        return {"messages": [("assistant", "Action executed successfully.")]}
    else:
        print("  [Security Gateway] DECLINED: Operation aborted.")
        return {"messages": [("assistant", "Action was cancelled by administrator.")]}


# ============================================================================
# 3. BUILDING THE SECURE GRAPH
# ============================================================================

def build_secure_graph():
    memory = MemorySaver()
    workflow = StateGraph(HITLState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("secure_action", secure_action_node)

    workflow.add_edge(START, "supervisor")
    
    # Conditional routing based on the 'action_pending' flag
    workflow.add_conditional_edges(
        "supervisor",
        lambda state: "secure_action" if state["action_pending"] else "end",
        {
            "secure_action": "secure_action",
            "end": END
        }
    )
    
    workflow.add_edge("secure_action", END)

    # Compile with persistence to support long-term pauses
    return workflow.compile(checkpointer=memory)


if __name__ == "__main__":
    print(f"\n{'='*75}\nMODULE 14: Human-in-the-Loop Supervision Demo\n{'='*75}")
    secure_app = build_secure_graph()
    thread_id = "hitl-test-01"
    config = {"configurable": {"thread_id": thread_id}}

    # Step 1: Initial Invocation
    print("\n[User] I want to purchase 100 shares of Apple.")
    res = secure_app.invoke({"messages": [HumanMessage(content="purchase 100 shares")]}, config=config)
    
    # In a real app, you would check if 'res' contains interrupts
    # and then prompt the user in the UI.
    
    print("\n--- SYSTEM PAUSED ---")
    print("Simulating human providing 'yes' via Command(resume='yes')")
    
    # Step 2: Resuming
    final_res = secure_app.invoke(Command(resume="yes"), config=config)
    print(f"\nFinal Bot Response: {final_res['messages'][-1].content}")
