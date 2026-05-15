"""
Module 13: Agentic RAG & Vector Search Logic
============================================

Implements a stateful RAG pipeline with relevance scoring, 
dynamic routing, and query rewriting loops.
"""

from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.messages import BaseMessage, HumanMessage
import operator

# ============================================================================
# 1. STATE DEFINITION
# ============================================================================

class RAGState(TypedDict):
    """
    Schema for Agentic RAG tracking retrieval quality and refinement cycles.
    """
    question: str
    documents: list[str]
    relevance_score: float
    final_answer: str


# ============================================================================
# 2. CORE NODES
# ============================================================================

def retrieve_node(state: RAGState) -> dict:
    """
    Fetches context from the vector database based on the current question.
    """
    print(f"  [Retriever] Scanning vector space for: '{state['question']}'")
    # Mocking retrieval results for demonstration
    mock_docs = ["LangGraph allows for cyclic graph execution.", "State is shared across nodes."]
    return {"documents": mock_docs}


def grade_documents_node(state: RAGState) -> dict:
    """
    Determines if the retrieved documents are relevant to the question.
    """
    print("  [Evaluator] Scoring document relevance...")
    # Simulating a relevance check (Agentic reasoning)
    score = 0.85 if "LangGraph" in state["question"] else 0.20
    return {"relevance_score": score}


def generate_node(state: RAGState) -> dict:
    """
    Generates a final answer using the filtered documents.
    """
    print("  [Generator] Synthesizing final response...")
    return {"final_answer": "LangGraph is a framework for building stateful agentic applications."}


def rewrite_query_node(state: RAGState) -> dict:
    """
    Refines the user's question if retrieval quality is low.
    """
    print("  [Rewriter] Low relevance detected. Optimizing query string...")
    return {"question": f"Detailed technical overview of {state['question']}"}


# ============================================================================
# 3. ROUTING LOGIC
# ============================================================================

def decide_to_generate(state: RAGState) -> Literal["generate", "rewrite"]:
    """
    Routes execution based on the relevance score threshold.
    """
    if state["relevance_score"] > 0.70:
        return "generate"
    else:
        return "rewrite"


# ============================================================================
# 4. BUILDING THE RAG GRAPH
# ============================================================================

def build_rag_graph():
    workflow = StateGraph(RAGState)

    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("grade", grade_documents_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("rewrite", rewrite_query_node)

    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "grade")
    
    workflow.add_conditional_edges(
        "grade",
        decide_to_generate,
        {
            "generate": "generate",
            "rewrite": "rewrite"
        }
    )
    
    workflow.add_edge("rewrite", "retrieve")
    workflow.add_edge("generate", END)

    return workflow.compile()


if __name__ == "__main__":
    print(f"\n{'='*75}\nMODULE 13: Agentic RAG & Vector Search Demo\n{'='*75}")
    rag_app = build_rag_graph()
    
    test_input = {"question": "LangGraph", "documents": [], "relevance_score": 0.0, "final_answer": ""}
    result = rag_app.invoke(test_input)
    print(f"\nFinal Result: {result['final_answer']}")
