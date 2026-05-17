import sqlite3
import os
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.sqlite import SqliteSaver

load_dotenv()
model = ChatOpenAI(model="gpt-4o-mini")

# 1. Define the State
# We add a 'user_profile' which acts as our Long-Term Memory storage
class State(MessagesState):
    user_profile: str

# 2. The Chatbot Node
def chatbot(state: State):
    """
    Combines Short-Term (Messages) with Long-Term (Profile)
    """
    profile = state.get("user_profile", "No previous information known.")
    
    # Inject Long-Term context into the system prompt
    system_prompt = SystemMessage(content=f"You are a helpful assistant. Here is what you remember about the user: {profile}")
    
    messages = [system_prompt] + state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}

# 3. The Memory Extraction Node (Long-Term Learning)
def reflect_on_memory(state: State):
    """
    Analyzes the conversation to extract long-term facts.
    This is how the agent 'learns' over time.
    """
    messages = state["messages"]
    current_profile = state.get("user_profile", "")
    
    # We ask the LLM to update the user profile based on the new messages
    prompt = f"""
    Update the user profile based on the recent conversation. 
    Current Profile: {current_profile}
    Recent Messages: {messages[-2:]}
    
    Output only the updated, concise profile.
    """
    
    updated_profile = model.invoke(prompt)
    return {"user_profile": updated_profile.content}

# 4. Build the Graph
workflow = StateGraph(State)

workflow.add_node("chatbot", chatbot)
workflow.add_node("reflect", reflect_on_memory)

workflow.add_edge(START, "chatbot")
workflow.add_edge("chatbot", "reflect")
workflow.add_edge("reflect", END)

# 5. Connect to a Persistent Database
# This creates a file 'memories.sqlite' that survives restarts!
db_path = "implement-short-term-memory/long-term-memory/memories.sqlite"
conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn)

app = workflow.compile(checkpointer=memory)

# --- Demonstration ---
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "user_123"}}
    
    print("\n--- Long-Term Memory Demo (Persisted in SQLite) ---")
    
    # Interaction 1
    user_input = "Hi! My name is Divyansh and I'm learning LangGraph. I love dark chocolate."
    print(f"\n[User]: {user_input}")
    output = app.invoke({"messages": [HumanMessage(content=user_input)]}, config)
    print(f"[Assistant]: {output['messages'][-1].content}")
    print(f"[Updated Long-Term Memory]: {output['user_profile']}")
    
    print("\n--- NOTE: Even if you kill this script, the data is now in 'memories.sqlite' ---")
    
    # Interaction 2 (Testing Recall)
    test_input = "Hey, what's my name and what do I like to eat?"
    print(f"\n[User]: {test_input}")
    output2 = app.invoke({"messages": [HumanMessage(content=test_input)]}, config)
    print(f"[Assistant]: {output2['messages'][-1].content}")
