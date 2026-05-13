"""
Production BMI Calculation Engine
Translates `1_bmi_workflow.ipynb` demonstrating pure-python state operations.
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END


class BMIState(TypedDict):
    """Shared state interface tracking parameters across node boundaries."""
    weight_kg: float
    height_m: float
    bmi: Optional[float]
    category: Optional[str]


def calculate_bmi(state: BMIState) -> BMIState:
    """Computes basic body mass index and overrides the 'bmi' key output."""
    weight = state["weight_kg"]
    height = state["height_m"]
    
    computed_bmi = weight / (height ** 2)
    return {"bmi": round(computed_bmi, 2)}


def label_bmi(state: BMIState) -> BMIState:
    """Classifies the derived BMI index into standard health categories."""
    bmi = state.get("bmi", 0.0)
    
    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 25.0:
        category = "Normal"
    elif 25.0 <= bmi < 30.0:
        category = "Overweight"
    else:
        category = "Obese"
        
    return {"category": category}


def compile_bmi_graph():
    """Builds nodes and edges to output a static executable app."""
    graph = StateGraph(BMIState)
    
    graph.add_node("calculate_bmi", calculate_bmi)
    graph.add_node("label_bmi", label_bmi)
    
    graph.add_edge(START, "calculate_bmi")
    graph.add_edge("calculate_bmi", "label_bmi")
    graph.add_edge("label_bmi", END)
    
    return graph.compile()


if __name__ == "__main__":
    workflow = compile_bmi_graph()
    
    initial_payload: BMIState = {
        "weight_kg": 75.0,
        "height_m": 1.80,
        "bmi": None,
        "category": None
    }
    
    print(f"--- Initializing BMI Workflow Execution ---")
    print(f"Input Data: {initial_payload}")
    
    final_output = workflow.invoke(initial_payload)
    
    print("\n[SUCCESS] Final Evaluated Graph State:")
    for k, v in final_output.items():
        print(f"  {k} -> {v}")
