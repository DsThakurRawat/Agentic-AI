"""
LangGraph Execution Model Internals Demonstration
Implements two heavy practical examples showcasing Superstep synchronous boundaries and MemorySaver Checkpointing.
"""

from typing import TypedDict, Literal, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver


# ============================================================================
# EXAMPLE 1: Superstep Synchronous Boundary State Processing Simulation
# ============================================================================

class SuperstepState(TypedDict):
    """Data interface tracking execution steps through isolated concurrent node runs."""
    base_counter: int
    execution_horizon_tag: Optional[str]


def worker_alpha_node(state: SuperstepState) -> dict:
    """Processor A: Accesses shared state parameter values inside Superstep bounds."""
    val = state["base_counter"]
    print(f"[Superstep Node A] Reading incoming base counter snapshot value: {val}")
    return {"execution_horizon_tag": "Thread Alpha Processed"}


def worker_beta_node(state: SuperstepState) -> dict:
    """Processor B: Processes identical incoming snapshots simultaneously."""
    val = state["base_counter"]
    print(f"[Superstep Node B] Reading identical input base counter snapshot value: {val}")
    return {"base_counter": val + 50}


def run_example_one():
    """Demonstrates parallel node operations reading unmutated base memory copies."""
    print(f"\n{'='*70}\nEXAMPLE 1: Superstep Synchronous Processing Boundary Flow\n{'='*70}")
    
    graph = StateGraph(SuperstepState)
    graph.add_node("alpha", worker_alpha_node)
    graph.add_node("beta", worker_beta_node)
    
    # Map parallel invocation paths running inside identical Superstep execution intervals
    graph.add_edge(START, "alpha")
    graph.add_edge(START, "beta")
    graph.add_edge("alpha", END)
    graph.add_edge("beta", END)
    
    app = graph.compile()
    
    initial_payload: SuperstepState = {"base_counter": 100, "execution_horizon_tag": None}
    print("Triggering parallel compilation processing steps...")
    
    output = app.invoke(initial_payload)
    print(f"\nFinal Audited Master Graph State Object Outcome:\n{output}")


# ============================================================================
# EXAMPLE 2: State Persistence Checkpointing utilizing MemorySaver
# ============================================================================

class PersistentThreadState(TypedDict):
    """Payload schema modeling persistent user conversation thread layers."""
    conversation_user: str
    inbound_message: str
    bot_reply_log: Optional[str]


def chatbot_policy_processor(state: PersistentThreadState) -> dict:
    """Updates target replies mimicking contextual policy update logic blocks."""
    msg = state["inbound_message"]
    user = state["conversation_user"]
    print(f"  [Chatbot Policy Engine] Processing inbound input context string: '{msg}'")
    
    reply = f"Hello {user}, evaluated query string '{msg}' and updated persistent state history."
    return {"bot_reply_log": reply}


def run_example_two():
    """Compiles persistent applications attaching MemorySaver long-term trackers."""
    print(f"\n{'='*70}\nEXAMPLE 2: Persistent Thread Checkpointing using MemorySaver\n{'='*70}")
    
    # 1. Instantiate explicit memory storage interface
    memory_backend = MemorySaver()
    
    graph = StateGraph(PersistentThreadState)
    graph.add_node("chatbot", chatbot_policy_processor)
    graph.add_edge(START, "chatbot")
    graph.add_edge("chatbot", END)
    
    # 2. Attach memory checkpointer targeting static compiler instances
    persistent_app = graph.compile(checkpointer=memory_backend)
    
    # 3. Configure distinct execution thread context dictionary mappings
    thread_config = {"configurable": {"thread_id": "thread_master_session_001"}}
    
    # Turn A: Submit initial processing instruction
    print("\n--- Execution Turn A: Initial Thread Invocation ---")
    payload_turn_a: PersistentThreadState = {
        "conversation_user": "Alice",
        "inbound_message": "Tell me my operational account clearance bounds.",
        "bot_reply_log": None
    }
    
    output_a = persistent_app.invoke(payload_turn_a, config=thread_config)
    print(f"Serialized Output Record Turn A:\n  {output_a['bot_reply_log']}")
    
    # Interrogate active persisted thread memory context snapshots directly
    persisted_checkpoint = persistent_app.get_state(thread_config)
    print(f"\nPolled Low-Level Persisted Checkpointer Snapshot Payload Values:\n{persisted_checkpoint.values}")
    
    # Turn B: Submit continuous context query sharing precise identical connection thread ID parameters
    print("\n--- Execution Turn B: Continuing Stateful Thread Memory Processing ---")
    payload_turn_b = {"inbound_message": "Can you provide standard summary documentation?"}
    
    output_b = persistent_app.invoke(payload_turn_b, config=thread_config)
    print(f"Serialized Output Record Turn B:\n  {output_b['bot_reply_log']}")


if __name__ == "__main__":
    run_example_one()
    run_example_two()
