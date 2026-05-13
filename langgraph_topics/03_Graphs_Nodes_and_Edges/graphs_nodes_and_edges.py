"""
Graphs, Nodes, and Edges Programmatic Demonstration
Implements two heavy practical examples showcasing static directed mappings and advanced conditional branching.
"""

from typing import TypedDict, Literal, Optional
from langgraph.graph import StateGraph, START, END


# ============================================================================
# EXAMPLE 1: Multi-Node Sequential Control Flow using Standard Edges
# ============================================================================

class StandardGraphState(TypedDict):
    """Payload definition mapping variables through linear graph layers."""
    base_metric: int
    computation_stage: Optional[str]


def initialization_node(state: StandardGraphState) -> dict:
    """Stage 1: Prepares raw baseline data structures."""
    print("[Node 1] Intercepting data streams to calculate base factors...")
    return {"base_metric": state["base_metric"] * 2, "computation_stage": "Initialized"}


def aggregation_node(state: StandardGraphState) -> dict:
    """Stage 2: Applies intermediate calculations over pre-compiled metrics."""
    print("[Node 2] Compiling enriched parameters into terminal output layers...")
    return {"base_metric": state["base_metric"] + 50, "computation_stage": "Finalized"}


def run_example_one():
    """Builds unconditional directed pipelines mapping persistent states."""
    print(f"\n{'='*70}\nEXAMPLE 1: Unconditional Standard Edge Flow\n{'='*70}")
    
    graph = StateGraph(StandardGraphState)
    graph.add_node("init", initialization_node)
    graph.add_node("aggregate", aggregation_node)
    
    # Establish direct directional execution loops
    graph.add_edge(START, "init")
    graph.add_edge("init", "aggregate")
    graph.add_edge("aggregate", END)
    
    app = graph.compile()
    
    initial_payload: StandardGraphState = {"base_metric": 25, "computation_stage": None}
    print(f"Inbound Initial Source Payload: {initial_payload}\n")
    
    output = app.invoke(initial_payload)
    print(f"\nFinal Evaluated Shared State Graph Object:\n{output}")


# ============================================================================
# EXAMPLE 2: Dynamic Decision Routing using Conditional Gatekeepers
# ============================================================================

class DecisionGraphState(TypedDict):
    """State tracking processing targets and dynamic evaluation outcomes."""
    system_load_index: float
    routing_destination: Optional[str]


def metric_sensor_node(state: DecisionGraphState) -> dict:
    """Simulates metric evaluation layers binding dynamic index variables."""
    load = state["system_load_index"]
    print(f"[Sensor Node] Polling core operational latency factors: Evaluated Index = {load}")
    return {}


def threshold_gatekeeper_router(state: DecisionGraphState) -> Literal["scale_up", "normal_track"]:
    """Conditional switching handler returning target destination string tags."""
    if state["system_load_index"] > 0.80:
        return "scale_up"
    else:
        return "normal_track"


def scale_up_node(state: DecisionGraphState) -> dict:
    """Emergency task path instantiating backup worker threads."""
    print("  [Gatekeeper Trigger: Track A] Critical threshold exceeded. Spinning up container clusters...")
    return {"routing_destination": "Auto-Scaling Cluster Provisioned"}


def normal_track_node(state: DecisionGraphState) -> dict:
    """Standard task path executing stable background jobs."""
    print("  [Gatekeeper Trigger: Track B] System stable. Continuing single-thread batch runs...")
    return {"routing_destination": "Stable Operation Maintained"}


def run_example_two():
    """Compiles advanced switching loops executing isolated destination code blocks."""
    print(f"\n{'='*70}\nEXAMPLE 2: Conditional Decision Branching Flow\n{'='*70}")
    
    graph = StateGraph(DecisionGraphState)
    graph.add_node("sensor", metric_sensor_node)
    graph.add_node("scale_up", scale_up_node)
    graph.add_node("normal_track", normal_track_node)
    
    graph.add_edge(START, "sensor")
    
    # Bind custom conditional interception handler
    graph.add_conditional_edges(
        "sensor",
        threshold_gatekeeper_router,
        {"scale_up": "scale_up", "normal_track": "normal_track"}
    )
    
    graph.add_edge("scale_up", END)
    graph.add_edge("normal_track", END)
    
    app = graph.compile()
    
    test_metrics = [0.95, 0.45]
    for idx, metric in enumerate(test_metrics, 1):
        print(f"\n--- Testing Runtime Payload Sequence #{idx} ---")
        initial_payload: DecisionGraphState = {"system_load_index": metric, "routing_destination": None}
        
        output = app.invoke(initial_payload)
        print(f"Final Resolved Output Target: {output['routing_destination']}")


if __name__ == "__main__":
    run_example_one()
    run_example_two()
