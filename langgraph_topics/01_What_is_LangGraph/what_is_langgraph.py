"""
LangGraph Framework Core Paradigm Demonstration
Implements two heavy practical examples showcasing static vs stateful graph routing logic.
"""

from typing import TypedDict, Literal, Optional
from langgraph.graph import StateGraph, START, END


# ============================================================================
# EXAMPLE 1: Static Linear Pipeline vs. Immutable Shared State Integration
# ============================================================================

class LinearState(TypedDict):
    """Data object storing variables across linear state execution nodes."""
    raw_query: str
    enriched_flag: bool
    summary_output: Optional[str]


def enrichment_processor(state: LinearState) -> dict:
    """Simulates context enrichment steps appending intermediate states."""
    print("[Pipeline Step 1] Intercepting data stream to execute context enrichment...")
    return {"enriched_flag": True}


def final_synthesis(state: LinearState) -> dict:
    """Reads enriched flags to output final targeted payload dictionaries."""
    print(f"[Pipeline Step 2] Reading verification state flag: Enriched={state.get('enriched_flag')}")
    output_str = f"Evaluated raw query: '{state['raw_query']}' successfully."
    return {"summary_output": output_str}


def run_example_one():
    """Compiles linear state pipelines mapping immutable dictionary structures."""
    print(f"\n{'='*70}\nEXAMPLE 1: Linear Stateful Transformation Flow\n{'='*70}")
    
    graph = StateGraph(LinearState)
    graph.add_node("enrich", enrichment_processor)
    graph.add_node("synthesize", final_synthesis)
    
    graph.add_edge(START, "enrich")
    graph.add_edge("enrich", "synthesize")
    graph.add_edge("synthesize", END)
    
    app = graph.compile()
    
    initial_payload: LinearState = {
        "raw_query": "Explain LangGraph immutable value replacement mechanics.",
        "enriched_flag": False,
        "summary_output": None
    }
    
    print(f"Initial Execution Input Payload:\n{initial_payload}\n")
    final_state = app.invoke(initial_payload)
    print(f"\nFinal Serialized Master Graph State Output:\n{final_state}")


# ============================================================================
# EXAMPLE 2: Dynamic Recursive Agent Self-Correction Optimization Loop
# ============================================================================

class AgentState(TypedDict):
    """Data interface leveraging iteration state trackers to bound loop cycles."""
    task_description: str
    current_attempt: int
    max_attempts: int
    audit_log: str


def reasoner_agent_node(state: AgentState) -> dict:
    """Executes reasoning logic incrementing internal computational loops."""
    attempt = state["current_attempt"] + 1
    print(f"  [Agent Iteration: Step #{attempt}] Executing task instructions...")
    
    updated_log = f"{state['audit_log']}\nCompleted reasoning loop interval #{attempt}."
    return {"current_attempt": attempt, "audit_log": updated_log.strip()}


def loop_router_condition(state: AgentState) -> Literal["reasoner_agent", "end"]:
    """Dynamic evaluation router loop enforcing recursion termination boundaries."""
    if state["current_attempt"] >= state["max_attempts"]:
        print("  [Gatekeeper Intercession] Maximum iteration cap reached. Forwarding to absolute terminal.")
        return "end"
    else:
        print("  [Gatekeeper Intercession] Validation threshold criteria unmet. Triggering self-correction refactoring loop.")
        return "reasoner_agent"


def run_example_two():
    """Builds and invokes recursive cyclic models with explicit gatekeepers."""
    print(f"\n{'='*70}\nEXAMPLE 2: Recursive Dynamic Self-Correction Loop\n{'='*70}")
    
    graph = StateGraph(AgentState)
    graph.add_node("reasoner_agent", reasoner_agent_node)
    
    graph.add_edge(START, "reasoner_agent")
    
    # Register dynamic loop routing interception maps
    graph.add_conditional_edges(
        "reasoner_agent",
        loop_router_condition,
        {"reasoner_agent": "reasoner_agent", "end": END}
    )
    
    app = graph.compile()
    
    initial_payload: AgentState = {
        "task_description": "Validate network security token authorization bounds.",
        "current_attempt": 0,
        "max_attempts": 3,
        "audit_log": "Engine initialized."
    }
    
    print(f"Inbound Initial Task Properties Payload:\n{initial_payload}\n")
    final_output = app.invoke(initial_payload)
    print(f"\nFinal Audited State Log Array Output:\n{final_output['audit_log']}")


if __name__ == "__main__":
    run_example_one()
    run_example_two()
