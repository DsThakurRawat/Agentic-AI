"""
Production Parallel Metrics Processing Engine
Translates `4_batsman_workflow.ipynb` demonstrating concurrent execution paths in LangGraph.
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END


class BatsmanState(TypedDict):
    """Data object encapsulating inputs and distinct parallel evaluation targets."""
    runs: int
    balls: int
    fours: int
    sixes: int
    
    sr: Optional[float]
    bpb: Optional[float]
    boundary_percent: Optional[float]
    summary: Optional[str]


def calculate_sr(state: BatsmanState) -> BatsmanState:
    """Computes strike rate metrics concurrently."""
    sr_metric = (state["runs"] / state["balls"]) * 100.0
    return {"sr": round(sr_metric, 2)}


def calculate_bpb(state: BatsmanState) -> BatsmanState:
    """Computes balls-per-boundary frequency concurrently."""
    total_boundaries = state["fours"] + state["sixes"]
    bpb_metric = state["balls"] / total_boundaries if total_boundaries > 0 else 0.0
    return {"bpb": round(bpb_metric, 2)}


def calculate_boundary_percent(state: BatsmanState) -> BatsmanState:
    """Computes boundary run percentage contribution concurrently."""
    boundary_runs = (state["fours"] * 4) + (state["sixes"] * 6)
    percentage = (boundary_runs / state["runs"]) * 100.0 if state["runs"] > 0 else 0.0
    return {"boundary_percent": round(percentage, 2)}


def summary_node(state: BatsmanState) -> BatsmanState:
    """Aggregates all computed parallel attributes into a unified text block."""
    compiled_summary = (
        f"\n--- BATTING METRICS SUMMARY ---\n"
        f"Strike Rate: {state.get('sr', 0.0)}\n"
        f"Balls Per Boundary: {state.get('bpb', 0.0)}\n"
        f"Boundary Runs Percentage: {state.get('boundary_percent', 0.0)}%\n"
        f"-------------------------------"
    )
    return {"summary": compiled_summary}


def compile_parallel_workflow():
    """Defines fork-join graph layout mapping concurrent paths."""
    graph = StateGraph(BatsmanState)
    
    # Register functional processors
    graph.add_node("calculate_sr", calculate_sr)
    graph.add_node("calculate_bpb", calculate_bpb)
    graph.add_node("calculate_boundary_percent", calculate_boundary_percent)
    graph.add_node("summary", summary_node)
    
    # Register parallel entry forks off START target
    graph.add_edge(START, "calculate_sr")
    graph.add_edge(START, "calculate_bpb")
    graph.add_edge(START, "calculate_boundary_percent")
    
    # Register downstream join barriers converging onto Summary
    graph.add_edge("calculate_sr", "summary")
    graph.add_edge("calculate_bpb", "summary")
    graph.add_edge("calculate_boundary_percent", "summary")
    
    graph.add_edge("summary", END)
    
    return graph.compile()


if __name__ == "__main__":
    workflow = compile_parallel_workflow()
    
    initial_payload: BatsmanState = {
        "runs": 100,
        "balls": 50,
        "fours": 6,
        "sixes": 4,
        "sr": None,
        "bpb": None,
        "boundary_percent": None,
        "summary": None
    }
    
    print("--- Initializing Concurrent Processing Engine ---")
    print(f"Inbound Metrics Payload: {initial_payload}")
    
    final_output = workflow.invoke(initial_payload)
    print(final_output["summary"])
