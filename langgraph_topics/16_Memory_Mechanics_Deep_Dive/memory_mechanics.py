"""
Module 16: Memory Mechanics Deep Dive
=====================================

Demonstrates the implementation of short-term thread memory
and cross-thread long-term semantic memory patterns.
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

# ============================================================================
# 1. STATE DEFINITION
# ============================================================================

class MemoryState(TypedDict):
    """
    Schema for stateful memory management.
    """
    messages: Annotated[list[BaseMessage], add_messages]
    summary: str  # Summarized memory to prevent context overflow
    user_preferences: dict  # Simulated long-term memory store


# ============================================================================
# 2. CORE MEMORY NODES
# ============================================================================

def summarize_history_node(state: MemoryState) -> dict:
    """
    Simulates a periodic summarization node that condenses the message history.
    This is essential for staying within token window limits.
    """
    msg_count = len(state["messages"])
    if msg_count > 5:
        print(f"  [Memory Manager] History length ({msg_count}) exceeds threshold. Summarizing...")
        new_summary = "The user is asking about agentic architectures and state management."
        # In a real app, you would delete old messages from the state here
        return {"summary": new_summary}
    return {}


def semantic_extractor_node(state: MemoryState) -> dict:
    """
    Extracts 'long-term' facts from the conversation to be stored in a 
    permanent user profile (simulated here as a dictionary).
    """
    last_msg = state["messages"][-1].content
    if "i like" in last_msg.lower():
        print("  [Memory Manager] Semantic fact detected. Updating long-term profile.")
        # Example: 'I like Python' -> {'coding_language': 'Python'}
        return {"user_preferences": {"coding_language": "Python"}}
    return {}


def chatbot_node(state: MemoryState) -> dict:
    """
    Generates a response using both short-term (messages) and 
    long-term (preferences + summary) context.
    """
    print("  [Chatbot] Generating response using integrated memory context...")
    return {"messages": [("assistant", "Understood. I've noted your preferences.")]}


# ============================================================================
# 3. BUILDING THE MEMORY-AWARE GRAPH
# ============================================================================

def build_memory_graph():
    builder = StateGraph(MemoryState)
    
    builder.add_node("chatbot", chatbot_node)
    builder.add_node("summarizer", summarize_history_node)
    builder.add_node("semantic_store", semantic_extractor_node)
    
    builder.add_edge(START, "chatbot")
    builder.add_edge("chatbot", "summarizer")
    builder.add_edge("summarizer", "semantic_store")
    builder.add_edge("semantic_store", END)
    
    return builder.compile()


if __name__ == "__main__":
    print(f"\n{'='*75}\nMODULE 16: Memory Mechanics & Persistence Demo\n{'='*75}")
    memory_app = build_memory_graph()
    
    test_input = {
        "messages": [HumanMessage(content="I like Python for building AI agents.")],
        "summary": "",
        "user_preferences": {}
    }
    
    result = memory_app.invoke(test_input)
    
    print("\nState Post-Execution:")
    print(f"  Summary: {result.get('summary', 'None')}")
    print(f"  Long-Term Preferences: {result.get('user_preferences', {})}")
