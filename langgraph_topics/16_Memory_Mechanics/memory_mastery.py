import os
import sqlite3
from typing import Annotated, TypedDict, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, trim_messages
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 1. STATE DEFINITIONS
# ==========================================

class MemoryState(TypedDict):
    # Base messages list
    messages: Annotated[List[BaseMessage], "The conversation history"]
    # For Summarization Pattern
    summary: str

# ==========================================
# 2. PATTERN A: TRIMMING (SHORT-TERM MEMORY)
# ==========================================
# Logic: Keep only the most recent N tokens/messages to fit the Context Window.

llm = ChatOpenAI(model="gpt-4o-mini")

def chatbot_node_trimming(state: MemoryState):
    # Trimming logic: Keep last 10 messages
    # In production, use langchain.messages.trim_messages for token-based trimming
    trimmed_history = state["messages"][-10:]
    
    response = llm.invoke(trimmed_history)
    return {"messages": [response]}

# ==========================================
# 3. PATTERN B: SUMMARIZATION (HYBRID MEMORY)
# ==========================================
# Logic: Summarize old messages and keep the summary + recent messages.

def summarize_history(state: MemoryState):
    summary = state.get("summary", "")
    if summary:
        # If summary exists, append new context to it
        summary_prompt = (
            f"This is a summary of the conversation to date: {summary}\n\n"
            f"Extend the summary by taking into account the new messages above."
        )
    else:
        summary_prompt = "Create a summary of the conversation above."

    messages = state["messages"] + [HumanMessage(content=summary_prompt)]
    response = llm.invoke(messages)
    
    # Keep the last 2 messages for immediate context, and delete the rest
    # to be replaced by the summary
    return {"summary": response.content, "messages": state["messages"][-2:]}

def chatbot_node_summary(state: MemoryState):
    summary = state.get("summary", "")
    if summary:
        system_message = f"Summary of conversation so far: {summary}"
        messages = [SystemMessage(content=system_message)] + state["messages"]
    else:
        messages = state["messages"]
        
    response = llm.invoke(messages)
    return {"messages": [response]}

# Conditional routing logic
def should_summarize(state: MemoryState):
    # Summarize if we have more than 6 messages
    if len(state["messages"]) > 6:
        return "summarize"
    return END

# ==========================================
# 4. PATTERN C: ADVANCED LTM EXTRACTION
# ==========================================
# Logic: Use a "Memory Node" to extract facts, deduplicate them, 
# and store them in a persistent BaseStore (InMemory or Postgres).

from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore
from pydantic import BaseModel, Field
import uuid

# Define the Memory Schema
class MemoryItem(BaseModel):
    text: str = Field(description="Atomic fact about the user")
    is_new: bool = Field(description="True if this is a NEW fact, False if duplicate")

class MemoryDecision(BaseModel):
    memories: List[MemoryItem] = Field(default_factory=list)

# The LTM Store (Can be PostgresStore in production)
ltm_store = InMemoryStore()

def memory_extraction_node(state: MemoryState, config: RunnableConfig, store: BaseStore):
    user_id = config["configurable"].get("user_id", "default_user")
    namespace = ("user", user_id, "facts")
    
    # 1. Retrieve existing memories for deduplication
    existing_items = store.search(namespace)
    existing_context = "\n".join([item.value["data"] for item in existing_items])
    
    # 2. Extract new facts from latest message
    extractor = llm.with_structured_output(MemoryDecision)
    last_msg = state["messages"][-1].content
    
    prompt = f"Existing Facts:\n{existing_context}\n\nNew Message: {last_msg}\nExtract only NEW facts."
    decision = extractor.invoke([SystemMessage(content=prompt)])
    
    # 3. Store only the facts marked as 'is_new'
    for memory in decision.memories:
        if memory.is_new:
            store.put(namespace, str(uuid.uuid4()), {"data": memory.text})
            
    return {} # Side-effect node (updates store, not state)

# ==========================================
# 5. PATTERN D: CLEAN STM DELETION
# ==========================================
# Logic: Instead of slicing, use RemoveMessage to tell the reducer to delete.

from langchain_core.messages import RemoveMessage

def cleanup_node(state: MemoryState):
    messages = state["messages"]
    # If history is too long, remove the oldest 2 messages
    if len(messages) > 10:
        return {"messages": [RemoveMessage(id=m.id) for m in messages[:2]]}
    return {}

# ==========================================
# 6. FINAL PERSISTENCE & EXECUTION
# ==========================================
# Initialize SQLite Checkpointer for STM
memory_db = sqlite3.connect("memory.sqlite", check_same_thread=False)
checkpointer = SqliteSaver(memory_db)

builder = StateGraph(MemoryState)
builder.add_node("chatbot", chatbot_node_summary)
builder.add_node("memory_extractor", memory_extraction_node)
builder.add_node("cleanup", cleanup_node)

builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", "memory_extractor")
builder.add_edge("memory_extractor", "cleanup")
builder.add_edge("cleanup", END)

# COMPILE WITH STORE (LTM) AND CHECKPOINTER (STM)
graph_app = builder.compile(checkpointer=checkpointer, store=ltm_store)

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "session_1", "user_id": "u1"}}
    
    # 1. First Turn: Identify user
    print("\n[Turn 1]")
    graph_app.invoke({"messages": [HumanMessage(content="Hi, I'm Divyansh and I love Python.")]}, config)
    
    # 2. Check LTM Store
    print("\n[Checking LTM Store]")
    facts = ltm_store.search(("user", "u1", "facts"))
    for f in facts: print(f"Stored Fact: {f.value['data']}")

    # 3. Second Turn: Deduplication Check
    print("\n[Turn 2 - Deduplication]")
    graph_app.invoke({"messages": [HumanMessage(content="Don't forget I am Divyansh.")]}, config)
    # The LLM should mark 'Divyansh' as is_new=False
