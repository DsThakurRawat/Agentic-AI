"""
LLM Workflows & Orchestration Topologies Demonstration
Implements two heavy functional examples showcasing Prompt Chaining and Dynamic Contextual Routing.
"""

from typing import TypedDict, Literal, Optional
from langgraph.graph import StateGraph, START, END


# ============================================================================
# EXAMPLE 1: Multi-Stage Prompt Chaining Transformation Sequence
# ============================================================================

class ChainingState(TypedDict):
    """Payload definition tracking structural plans and resulting body content."""
    user_topic: str
    structural_outline: Optional[str]
    final_output_body: Optional[str]


def outline_planning_node(state: ChainingState) -> dict:
    """Phase 1: Synthesizes high-level outline architecture mapping target fields."""
    topic = state["user_topic"]
    print(f"[Phase 1: Planning] Constructing targeted master outline for topic: '{topic}'")
    
    generated_outline = f"1. Executive Abstract\n2. Deep Technical Breakdown\n3. Verification Suite"
    return {"structural_outline": generated_outline}


def content_expansion_node(state: ChainingState) -> dict:
    """Phase 2: Reads synthesized master outline payloads to author complete bodies."""
    outline = state["structural_outline"]
    print("[Phase 2: Authoring] Expanding intermediate structural outline into rich final documents...")
    
    final_body = f"--- START GENERATED DOCUMENT ---\nFollowed target blueprint:\n{outline}\n--- END GENERATED DOCUMENT ---"
    return {"final_output_body": final_body}


def run_example_one():
    """Compiles sequential multi-stage dependency map applications."""
    print(f"\n{'='*70}\nEXAMPLE 1: Multi-Stage Prompt Chaining Flow\n{'='*70}")
    
    graph = StateGraph(ChainingState)
    graph.add_node("plan", outline_planning_node)
    graph.add_node("expand", content_expansion_node)
    
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "expand")
    graph.add_edge("expand", END)
    
    app = graph.compile()
    
    initial_payload: ChainingState = {
        "user_topic": "Agentic Design Patterns in Python",
        "structural_outline": None,
        "final_output_body": None
    }
    
    output = app.invoke(initial_payload)
    print(f"\nCompleted Output Document:\n{output['final_output_body']}")


# ============================================================================
# EXAMPLE 2: Dynamic Semantic Support Routing Interception Pipeline
# ============================================================================

class RoutingState(TypedDict):
    """Context tracking issue inputs, target diagnostic fields, and tailored resolutions."""
    client_issue: str
    classification_tag: Literal["Technical", "Billing"]
    resolution_payload: Optional[str]


def triage_classifier_node(state: RoutingState) -> dict:
    """Simulates upfront categorization steps binding contextual tags."""
    issue = state["client_issue"]
    print(f"[Triage Node] Parsing semantic context for issue string: '{issue[:40]}...'")
    
    # Static runtime emulation assignment logic
    tag = "Technical" if "socket" in issue.lower() else "Billing"
    print(f"  Assigned Master Classification Tag: {tag}")
    return {"classification_tag": tag}


def routing_switch_interception(state: RoutingState) -> Literal["resolve_technical", "resolve_billing"]:
    """Dynamic evaluation router mapping scalar strings targeting target downstream nodes."""
    if state["classification_tag"] == "Technical":
        return "resolve_technical"
    else:
        return "resolve_billing"


def resolve_technical_node(state: RoutingState) -> dict:
    """Functional task routine resolving highly complex technical stack errors."""
    print("[Downstream Track A] Executing custom Senior Architecture debugging scripts...")
    return {"resolution_payload": "Issued emergency socket connection pooling retry hotfix."}


def resolve_billing_node(state: RoutingState) -> dict:
    """Functional task routine generating standard account adjustments."""
    print("[Downstream Track B] Authoring account adjustment ledger credits...")
    return {"resolution_payload": "Credited $50 account allowance ledger reconciliation."}


def run_example_two():
    """Builds conditional execution map models running distinct isolated pathways."""
    print(f"\n{'='*70}\nEXAMPLE 2: Dynamic Semantic Support Routing Flow\n{'='*70}")
    
    graph = StateGraph(RoutingState)
    graph.add_node("triage", triage_classifier_node)
    graph.add_node("resolve_technical", resolve_technical_node)
    graph.add_node("resolve_billing", resolve_billing_node)
    
    graph.add_edge(START, "triage")
    
    # Register conditional switching interceptor
    graph.add_conditional_edges(
        "triage",
        routing_switch_interception,
        {"resolve_technical": "resolve_technical", "resolve_billing": "resolve_billing"}
    )
    
    graph.add_edge("resolve_technical", END)
    graph.add_edge("resolve_billing", END)
    
    app = graph.compile()
    
    test_cases = [
        {"client_issue": "Socket timeout exception during high load test cycles.", "classification_tag": "Technical"},
        {"client_issue": "Invoice total evaluated incorrect platform unit usage charges.", "classification_tag": "Billing"}
    ]
    
    for idx, tc in enumerate(test_cases, 1):
        print(f"\n--- Running Pipeline Stream #{idx} ---")
        initial_payload: RoutingState = {
            "client_issue": tc["client_issue"],
            "classification_tag": tc["classification_tag"],
            "resolution_payload": None
        }
        
        output = app.invoke(initial_payload)
        print(f"Final Resolved Triage Output: {output['resolution_payload']}")


if __name__ == "__main__":
    run_example_one()
    run_example_two()
