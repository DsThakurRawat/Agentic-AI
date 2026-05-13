"""
Production Dynamic Conditional Routing Engine
Translates `6_quadratic_equation_workflow.ipynb` demonstrating explicit edge routing in LangGraph.
"""

from typing import TypedDict, Literal, Optional
from langgraph.graph import StateGraph, START, END


class QuadState(TypedDict):
    """Shared state dictionary mapping root parameters and execution trajectories."""
    a: int
    b: int
    c: int
    
    equation: Optional[str]
    discriminant: Optional[float]
    result: Optional[str]


def show_equation(state: QuadState) -> QuadState:
    """Formats string representation of target quadratic formulas."""
    formatted_eq = f"{state['a']}x² + {state['b']}x + {state['c']}"
    return {"equation": formatted_eq}


def calculate_discriminant(state: QuadState) -> QuadState:
    """Derives mathematical discriminant envelope from state coefficients."""
    d_val = (state["b"] ** 2) - (4 * state["a"] * state["c"])
    return {"discriminant": float(d_val)}


def real_roots_node(state: QuadState) -> QuadState:
    """Executes root evaluations for distinct real positive cases."""
    d_root = state["discriminant"] ** 0.5
    r1 = (-state["b"] + d_root) / (2 * state["a"])
    r2 = (-state["b"] - d_root) / (2 * state["a"])
    return {"result": f"Real distinct roots evaluated: {round(r1, 2)} and {round(r2, 2)}"}


def repeated_roots_node(state: QuadState) -> QuadState:
    """Executes root evaluation for singular zero discriminant cases."""
    r = (-state["b"]) / (2 * state["a"])
    return {"result": f"Single repeated real root evaluated: {round(r, 2)}"}


def no_real_roots_node(state: QuadState) -> QuadState:
    """Handles logic mapping complex negative discriminant pathways."""
    return {"result": "No real roots exist (Complex roots region domain)"}


def check_condition_router(state: QuadState) -> Literal["real_roots", "repeated_roots", "no_real_roots"]:
    """Conditional evaluation router function outputting explicit target string targets."""
    d_val = state["discriminant"]
    
    if d_val > 0:
        return "real_roots"
    elif d_val == 0:
        return "repeated_roots"
    else:
        return "no_real_roots"


def compile_conditional_router():
    """Builds conditional dynamic graph maps."""
    graph = StateGraph(QuadState)
    
    graph.add_node("show_equation", show_equation)
    graph.add_node("calculate_discriminant", calculate_discriminant)
    graph.add_node("real_roots", real_roots_node)
    graph.add_node("repeated_roots", repeated_roots_node)
    graph.add_node("no_real_roots", no_real_roots_node)
    
    graph.add_edge(START, "show_equation")
    graph.add_edge("show_equation", "calculate_discriminant")
    
    # Register dynamic routing interception mapping
    graph.add_conditional_edges("calculate_discriminant", check_condition_router)
    
    graph.add_edge("real_roots", END)
    graph.add_edge("repeated_roots", END)
    graph.add_edge("no_real_roots", END)
    
    return graph.compile()


if __name__ == "__main__":
    workflow = compile_conditional_router()
    
    test_cases = [
        {"a": 1, "b": -3, "c": 2},  # D = 9 - 8 = 1 > 0 -> Real roots
        {"a": 1, "b": -2, "c": 1},  # D = 4 - 4 = 0 -> Repeated roots
        {"a": 1, "b": 1, "c": 1}    # D = 1 - 4 = -3 < 0 -> No real roots
    ]
    
    print("--- Testing Dynamic Conditional Router Processing ---")
    for idx, payload in enumerate(test_cases, 1):
        initial_state: QuadState = {
            "a": payload["a"],
            "b": payload["b"],
            "c": payload["c"],
            "equation": None,
            "discriminant": None,
            "result": None
        }
        
        print(f"\nEvaluating Input Stream #{idx}: a={payload['a']}, b={payload['b']}, c={payload['c']}")
        output = workflow.invoke(initial_state)
        print(f"  Target Equation Formatted: {output['equation']}")
        print(f"  Computed Discriminant: {output['discriminant']}")
        print(f"  Final Resolved Outcome: {output['result']}")
