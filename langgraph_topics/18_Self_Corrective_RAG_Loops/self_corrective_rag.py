"""
Module 18: Self-Corrective RAG (CRAG & Self-RAG)
==============================================

Demonstrates advanced retrieval loops with web fallback,
hallucination grading, and iterative refinement.
"""

from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, START, END

# ============================================================================
# 1. STATE DEFINITION
# ============================================================================

class CorrectiveRAGState(TypedDict):
    """
    Schema for tracking retrieval quality and hallucination status.
    """
    question: str
    generation: str
    documents: list[str]
    is_hallucination: bool
    retrieval_quality: Literal["high", "low", "ambiguous"]


# ============================================================================
# 2. CORE ADVANCED RAG NODES
# ============================================================================

def retrieve_node(state: CorrectiveRAGState) -> dict:
    """Fetches documents from internal Vector Store."""
    print("  [Step 1: Retrieval] Fetching documents from internal index...")
    return {"documents": ["LangGraph supports cyclic execution."]}


def grade_documents_node(state: CorrectiveRAGState) -> dict:
    """Evaluates if the retrieved docs actually answer the question."""
    print("  [Step 2: Grading] Assessing retrieval quality...")
    # Mocking quality assessment
    quality = "high" if "LangGraph" in state["question"] else "low"
    return {"retrieval_quality": quality}


def web_search_node(state: CorrectiveRAGState) -> dict:
    """Fallback node for when internal retrieval fails."""
    print("  [Step 2 (Fallback): Web Search] Internal docs low quality. Fetching via Tavily...")
    return {"documents": ["Web result: LangGraph is built on LangChain."]}


def generate_node(state: CorrectiveRAGState) -> dict:
    """Synthesizes the final answer."""
    print("  [Step 3: Generation] Generating answer from context...")
    return {"generation": "LangGraph is a framework for stateful agents."}


def hallucination_grader_node(state: CorrectiveRAGState) -> dict:
    """Checks if the generation is supported by the documents."""
    print("  [Step 4: Critique] Checking for hallucinations...")
    # Logic: Does 'generation' claim anything not in 'documents'?
    is_hallucination = False
    return {"is_hallucination": is_hallucination}


# ============================================================================
# 3. ADVANCED ROUTING LOGIC
# ============================================================================

def decide_retrieval_path(state: CorrectiveRAGState) -> Literal["generate", "web_search"]:
    """Routes based on retrieval quality."""
    if state["retrieval_quality"] == "high":
        return "generate"
    else:
        return "web_search"


def decide_finish(state: CorrectiveRAGState) -> Literal["finish", "regenerate"]:
    """Routes based on hallucination check."""
    if state["is_hallucination"]:
        return "regenerate"
    else:
        return "finish"


# ============================================================================
# 4. BUILDING THE SELF-CORRECTIVE GRAPH
# ============================================================================

def build_crag_graph():
    workflow = StateGraph(CorrectiveRAGState)
    
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("grade_docs", grade_documents_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("critique", hallucination_grader_node)
    
    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "grade_docs")
    
    workflow.add_conditional_edges(
        "grade_docs",
        decide_retrieval_path,
        {
            "generate": "generate",
            "web_search": "web_search"
        }
    )
    
    workflow.add_edge("web_search", "generate")
    workflow.add_edge("generate", "critique")
    
    workflow.add_conditional_edges(
        "critique",
        decide_finish,
        {
            "finish": END,
            "regenerate": "generate"
        }
    )
    
    return workflow.compile()


if __name__ == "__main__":
    print(f"\n{'='*75}\nMODULE 18: Self-Corrective RAG (CRAG/Self-RAG) Demo\n{'='*75}")
    crag_app = build_crag_graph()
    
    test_input = {"question": "What is LangGraph?", "generation": "", "documents": [], "is_hallucination": False, "retrieval_quality": "low"}
    result = crag_app.invoke(test_input)
    
    print("\nFinal Result:")
    print(f"  Generation: {result['generation']}")
    print(f"  Hallucination Detected: {result['is_hallucination']}")
