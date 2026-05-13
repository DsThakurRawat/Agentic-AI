"""
Production Simple LLM Task Processing
Translates `2_simple_llm_workflow.ipynb` embedding ChatOpenAI inside graph nodes.
"""

import os
from typing import TypedDict, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END


class LLMState(TypedDict):
    """Context container tracking input questions and generated completions."""
    question: str
    answer: Optional[str]


def llm_qa_node(state: LLMState) -> LLMState:
    """Invokes ChatOpenAI models formatting explicit instruction envelopes."""
    load_dotenv()
    
    # Initialize target model; uses active OPENAI_API_KEY env key configuration.
    model = ChatOpenAI(temperature=0.0)
    
    question = state["question"]
    print(f"[Engine Execution] Submitting query to LLM: '{question}'")
    
    prompt = f"Answer the following query concisely:\n{question}"
    generated_content = model.invoke(prompt).content
    
    return {"answer": generated_content}


def compile_llm_app():
    """Builds singular routing edges to output runnable targets."""
    graph = StateGraph(LLMState)
    
    graph.add_node("llm_qa", llm_qa_node)
    graph.add_edge(START, "llm_qa")
    graph.add_edge("llm_qa", END)
    
    return graph.compile()


if __name__ == "__main__":
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("[CAUTION] OPENAI_API_KEY environment variable missing.")
        
    workflow = compile_llm_app()
    
    initial_payload: LLMState = {
        "question": "What is the primary benefit of encapsulating state variables inside LangGraph TypedDict schemas?",
        "answer": None
    }
    
    try:
        final_state = workflow.invoke(initial_payload)
        print(f"\n[MODEL OUTPUT]\n{final_state['answer']}")
    except Exception as e:
        print(f"Execution Error: {e}")
