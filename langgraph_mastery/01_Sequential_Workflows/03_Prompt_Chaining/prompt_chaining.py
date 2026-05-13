"""
Production Multi-Stage Prompt Chaining Pipeline
Translates `3_prompt_chaining.ipynb` sequencing discrete outline synthesis and content authoring steps.
"""

import os
from typing import TypedDict, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END


class BlogState(TypedDict):
    """Data interface tracking title inputs, outline stages, and finished text content."""
    title: str
    outline: Optional[str]
    content: Optional[str]


def create_outline(state: BlogState) -> BlogState:
    """Invokes LLM planning routines to output a rich structured markdown outline."""
    load_dotenv()
    model = ChatOpenAI(temperature=0.2)
    
    title = state["title"]
    print(f"[Phase 1] Synthesizing structural outline for title: '{title}'...")
    
    prompt = f"Generate a comprehensive markdown outline for a technical blog titled: '{title}'"
    generated_outline = model.invoke(prompt).content
    
    return {"outline": generated_outline}


def create_blog(state: BlogState) -> BlogState:
    """Reads both the initial title and intermediate outline to author full blog text."""
    load_dotenv()
    model = ChatOpenAI(temperature=0.4)
    
    title = state["title"]
    outline = state["outline"]
    
    print(f"[Phase 2] Expanding generated outline into full comprehensive text...")
    
    prompt = (
        f"Write a highly detailed technical blog on the topic: '{title}'.\n"
        f"You must strictly follow this exact structural outline:\n\n{outline}"
    )
    final_content = model.invoke(prompt).content
    
    return {"content": final_content}


def compile_chaining_workflow():
    """Assembles prompt stages into a continuous linear chain workflow."""
    graph = StateGraph(BlogState)
    
    graph.add_node("create_outline", create_outline)
    graph.add_node("create_blog", create_blog)
    
    graph.add_edge(START, "create_outline")
    graph.add_edge("create_outline", "create_blog")
    graph.add_edge("create_blog", END)
    
    return graph.compile()


if __name__ == "__main__":
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("[CAUTION] OPENAI_API_KEY is not configured in environment variables.")
        
    workflow = compile_chaining_workflow()
    
    initial_payload: BlogState = {
        "title": "Architecting Scalable Multi-Agent AI Workflows in Python",
        "outline": None,
        "content": None
    }
    
    try:
        final_state = workflow.invoke(initial_payload)
        print("\n" + "="*50)
        print(f"OUTLINE SNAPSHOT:")
        print("="*50)
        print(final_state["outline"])
        
        print("\n" + "="*50)
        print(f"FINAL GENERATED CONTENT BODY:")
        print("="*50)
        print(final_state["content"])
    except Exception as e:
        print(f"Pipeline Runtime Exception: {e}")
