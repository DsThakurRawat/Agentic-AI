from typing import Annotated, TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, trim_messages
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import InMemorySaver

# 1. Setup environment and model
load_dotenv()
model = ChatOpenAI(model="gpt-4o-mini")

# 2. Define the Trimming Logic
# Short-term memory needs management to stay within context limits.
# Here we keep only the last 10 messages.
trimmer = trim_messages(
    max_tokens=1000,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human",
)

# 3. Define the Node logic
def chatbot_node(state: MessagesState):
    """
    Processes the current state, trims history to simulate 
    'short-term' constraints, and gets a response from the LLM.
    """
    # Trim messages to keep the context window clean
    trimmed_messages = trimmer.invoke(state["messages"])
    
    # Get response from model
    response = model.invoke(trimmed_messages)
    
    # Return the new message to be appended to the state
    return {"messages": [response]}

# 4. Build the Graph
workflow = StateGraph(MessagesState)

# Add the chatbot node
workflow.add_node("chatbot", chatbot_node)

# Set entry and exit points
workflow.add_edge(START, "chatbot")
workflow.add_edge("chatbot", END)

# 5. Add Persistence (The 'Memory' part)
# InMemorySaver allows the graph to remember state across multiple .invoke() calls 
# for the same thread_id.
memory = InMemorySaver()
app = workflow.compile(checkpointer=memory)

# 6. Demonstration
if __name__ == "__main__":
    print("\n--- LangGraph Short-Term Memory Demo ---")
    
    # Thread config defines the 'conversation session'
    config = {"configurable": {"thread_id": "session_1"}}
    
    # First Interaction
    print("\n[User]: Hi! I'm Antigravity, and I love coding.")
    input_1 = {"messages": [HumanMessage(content="Hi! I'm Antigravity, and I love coding.")]}
    for chunk in app.stream(input_1, config, stream_mode="values"):
        last_message = chunk["messages"][-1]
        if isinstance(last_message, AIMessage):
            print(f"[Assistant]: {last_message.content}")

    # Second Interaction (Demonstrating Memory)
    print("\n[User]: What is my name and what do I like?")
    input_2 = {"messages": [HumanMessage(content="What is my name and what do I like?")]}
    for chunk in app.stream(input_2, config, stream_mode="values"):
        last_message = chunk["messages"][-1]
        if isinstance(last_message, AIMessage):
            print(f"[Assistant]: {last_message.content}")
    
    # Third Interaction (Different thread - No memory)
    print("\n--- Testing Thread Isolation (New Session) ---")
    config_new = {"configurable": {"thread_id": "session_2"}}
    print("[User]: Do you know my name?")
    input_3 = {"messages": [HumanMessage(content="Do you know my name?")]}
    for chunk in app.stream(input_3, config_new, stream_mode="values"):
        last_message = chunk["messages"][-1]
        if isinstance(last_message, AIMessage):
            print(f"[Assistant]: {last_message.content}")
