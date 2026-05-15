"""
Module 15: Subgraphs Orchestration & Encapsulation
==================================================

Demonstrates how to encapsulate a complete StateGraph as a modular node
within a larger parent orchestrator graph.
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# ============================================================================
# 1. THE SUBGRAPH (Translation Engine)
# ============================================================================

class SubState(TypedDict):
    """Local state schema for the translation subgraph."""
    input_text: str
    translated_text: str


def translate_node(state: SubState) -> dict:
    """Simulates a translation process."""
    print(f"  [Subgraph: Translation] Translating to Hindi: '{state['input_text']}'")
    return {"translated_text": f"[HINDI] {state['input_text']}"}


# Compile the subgraph independently
subgraph_builder = StateGraph(SubState)
subgraph_builder.add_node("translate", translate_node)
subgraph_builder.add_edge(START, "translate")
subgraph_builder.add_edge("translate", END)
compiled_subgraph = subgraph_builder.compile()


# ============================================================================
# 2. THE PARENT GRAPH (Content Orchestrator)
# ============================================================================

class ParentState(TypedDict):
    """Global state schema for the parent orchestrator."""
    topic: str
    content_eng: str
    content_hin: str


def research_node(state: ParentState) -> dict:
    """Simulates a research phase generating English content."""
    print(f"  [Parent: Researcher] Generating English draft for: '{state['topic']}'")
    return {"content_eng": f"Technical deep dive on {state['topic']}."}


def call_subgraph_node(state: ParentState) -> dict:
    """
    This is the BRIDGE NODE. It invokes the compiled subgraph 
    and maps the results back to the parent state.
    """
    print("  [Parent] Delegating translation to Subgraph...")
    
    # Map Parent State -> Subgraph State
    sub_input = {"input_text": state["content_eng"]}
    
    # Invoke the Subgraph
    sub_result = compiled_subgraph.invoke(sub_input)
    
    # Map Subgraph Result -> Parent State
    return {"content_hin": sub_result["translated_text"]}


# ============================================================================
# 3. BUILDING THE ORCHESTRATOR
# ============================================================================

def build_orchestrator():
    parent_builder = StateGraph(ParentState)
    
    parent_builder.add_node("research", research_node)
    parent_builder.add_node("translate_subgraph", call_subgraph_node)
    
    parent_builder.add_edge(START, "research")
    parent_builder.add_edge("research", "translate_subgraph")
    parent_builder.add_edge("translate_subgraph", END)
    
    return parent_builder.compile()


if __name__ == "__main__":
    print(f"\n{'='*75}\nMODULE 15: Subgraphs Orchestration Demo\n{'='*75}")
    orchestrator = build_orchestrator()
    
    test_input = {"topic": "Multi-Agent Systems", "content_eng": "", "content_hin": ""}
    result = orchestrator.invoke(test_input)
    
    print("\nFinal Orchestration Result:")
    print(f"  Topic: {result['topic']}")
    print(f"  English Content: {result['content_eng']}")
    print(f"  Hindi Content: {result['content_hin']}")
