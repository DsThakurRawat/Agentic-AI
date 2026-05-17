import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, trim_messages
from langgraph.graph import StateGraph, START, END, MessagesState

load_dotenv()

# We'll use a model with a known context limit
model = ChatOpenAI(model="gpt-4o-mini")

# --- CASE 1: THE NAIVE APPROACH (Will eventually crash or become too expensive) ---
def naive_chatbot(state: MessagesState):
    """
    This node simply passes ALL messages to the model.
    If the conversation is long enough (e.g. 50+ messages), 
    this will eventually hit the 'Context Overflow' error.
    """
    print(f"DEBUG: Processing {len(state['messages'])} messages...")
    response = model.invoke(state["messages"])
    return {"messages": [response]}

# --- CASE 2: THE MANAGED APPROACH (The Solution) ---
# We define a trimmer to prevent overflow
trimmer = trim_messages(
    max_tokens=2000, # Strict limit to prevent overflow
    strategy="last",
    token_counter=model,
    include_system=True,
    start_on="human",
)

def managed_chatbot(state: MessagesState):
    """
    This node TRIMS the history before sending it to the model.
    It solves the Context Overflow problem by only keeping the 
    most relevant 'Short-Term' history.
    """
    trimmed = trimmer.invoke(state["messages"])
    print(f"DEBUG: Total messages: {len(state['messages'])} | Sent to LLM: {len(trimmed)}")
    response = model.invoke(trimmed)
    return {"messages": [response]}

def run_simulation(is_managed=False):
    workflow = StateGraph(MessagesState)
    node_func = managed_chatbot if is_managed else naive_chatbot
    workflow.add_node("chatbot", node_func)
    workflow.add_edge(START, "chatbot")
    workflow.add_edge("chatbot", END)
    app = workflow.compile()

    # Simulate a long conversation
    print(f"\n--- Running {'MANAGED' if is_managed else 'NAIVE'} Simulation ---")
    state = {"messages": []}
    for i in range(5): # Imagine this is 50 in a real app
        state["messages"].append(HumanMessage(content=f"This is message number {i}. Remember the secret key: {12345 + i}"))
        state = app.invoke(state)
        print(f"Step {i+1} complete.")

if __name__ == "__main__":
    # In a real scenario, you'd see the 'Naive' one get slower and eventually crash.
    # The 'Managed' one would stay consistent in speed and token usage.
    run_simulation(is_managed=False)
    run_simulation(is_managed=True)
