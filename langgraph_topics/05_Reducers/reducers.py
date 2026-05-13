"""
State Reducers & Parallel Aggregation Demonstration
Implements two heavy functional examples showcasing operator.add list appending and custom mathematical reduction.
"""

import operator
from typing import TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, START, END


# ============================================================================
# EXAMPLE 1: Parallel Thread Forking leveraging operator.add Reducers
# ============================================================================

class ParallelReducerState(TypedDict):
    """Payload container utilizing custom list reducers to merge parallel threads."""
    job_guid: str
    
    # operator.add appends list items without destructive memory overrides
    evaluation_audits: Annotated[list[str], operator.add]
    final_compiled_summary: Optional[str]


def parallel_worker_one(state: ParallelReducerState) -> dict:
    """Thread A: Executes distinct concurrent database validation tasks."""
    print("[Thread A] Executing isolated memory allocation audit routines...")
    return {"evaluation_audits": ["Thread A Check: Memory Bounds Allocated Cleanly"]}


def parallel_worker_two(state: ParallelReducerState) -> dict:
    """Thread B: Executes distinct concurrent network layer connectivity polls."""
    print("[Thread B] Polling underlying cluster socket stability metrics...")
    return {"evaluation_audits": ["Thread B Check: Socket Latency Nominal"]}


def downstream_consensus_join(state: ParallelReducerState) -> dict:
    """Consensus barrier node: Accesses completely concatenated reducer list arrays."""
    audits = state["evaluation_audits"]
    print(f"\n[Consensus Join Barrier] Aggregating completed parallel evaluation arrays:\n{audits}")
    
    summary = f"Consensus successfully verified {len(audits)} distinct concurrent operational factors."
    return {"final_compiled_summary": summary}


def run_example_one():
    """Compiles concurrent map networks safely leveraging reduction contracts."""
    print(f"\n{'='*70}\nEXAMPLE 1: Parallel operator.add List Reduction Flow\n{'='*70}")
    
    graph = StateGraph(ParallelReducerState)
    graph.add_node("workerA", parallel_worker_one)
    graph.add_node("workerB", parallel_worker_two)
    graph.add_node("consensus", downstream_consensus_join)
    
    # Establish parallel Fan-Out execution forks
    graph.add_edge(START, "workerA")
    graph.add_edge(START, "workerB")
    
    # Register join synchronization edges
    graph.add_edge("workerA", "consensus")
    graph.add_edge("workerB", "consensus")
    graph.add_edge("consensus", END)
    
    app = graph.compile()
    
    initial_payload: ParallelReducerState = {
        "job_guid": "GUID_PARALLEL_RUN_77",
        "evaluation_audits": [],
        "final_compiled_summary": None
    }
    
    output = app.invoke(initial_payload)
    print(f"\nFinal Serialized Master Output Statement:\n{output['final_compiled_summary']}")


# ============================================================================
# EXAMPLE 2: Custom Function Reduction Logic mapping Numerical Metrics
# ============================================================================

def custom_sum_reducer(current_val: int, new_val: int) -> int:
    """Custom reduction logic function performing mathematical sum operations."""
    print(f"  [Custom Reducer Backend] Merging values: Base={current_val} + Update={new_val}")
    return current_val + new_val


class CustomNumericState(TypedDict):
    """Schema tracking variables mapping explicit functional parameter reducers."""
    process_title: str
    
    # Explicit custom reduction function assignment
    accumulated_throughput: Annotated[int, custom_sum_reducer]


def throughput_feeder_node(state: dict) -> dict:
    """Simulates runtime metrics updating base reduction keys directly."""
    print("[Feeder Node] Injecting new raw streaming packet payload counts...")
    return {"accumulated_throughput": 350}


def run_example_two():
    """Demonstrates pure python programmatic custom parameter reduction."""
    print(f"\n{'='*70}\nEXAMPLE 2: Custom Function Parameter Reduction Flow\n{'='*70}")
    
    # Emulating local compilation update processing routines
    base_state: CustomNumericState = {"process_title": "Packet Stream Core", "accumulated_throughput": 1200}
    
    print(f"Initial State Properties Snapshot: Throughput = {base_state['accumulated_throughput']}")
    
    # Triggering functional node returning explicit subset dictionary updates
    node_return = throughput_feeder_node(base_state)
    
    # Emulating framework runtime reducer extraction
    resolved_val = custom_sum_reducer(base_state["accumulated_throughput"], node_return["accumulated_throughput"])
    print(f"Final Resolved Accumulation Master Key Outcome: {resolved_val}")


if __name__ == "__main__":
    run_example_one()
    run_example_two()
