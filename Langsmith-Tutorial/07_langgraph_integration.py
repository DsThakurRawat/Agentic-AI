import os
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END

"""
Module 4: Agentic Frameworks & Production Features

Topic: LangGraph + LangSmith Integration

LangGraph is designed for cyclical, stateful AI agents. Tracing is absolutely 
mandatory here because an agent might loop multiple times, calling tools over 
and over. 

LangSmith treats LangGraph natively: it will visualize the Graph structure and 
group all loops under a single parent run.
"""

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "LangSmith-Masterclass-LangGraph"

# 1. Define Agent State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# 2. Define Nodes
def agent_node(state: AgentState):
    print("--- NODE: Agent Processing ---")
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    # Simple reflection: the agent will respond to the messages
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def guardrail_node(state: AgentState):
    print("--- NODE: Guardrail Check ---")
    last_msg = state["messages"][-1].content.lower()
    if "secret" in last_msg:
        # Override the agent's response if it tries to leak a secret
        from langchain_core.messages import AIMessage
        return {"messages": [AIMessage(content="I cannot provide that information.")]}
    return {"messages": []} # No change

def run_langgraph_trace():
    print("Compiling LangGraph StateMachine...")
    # Build Graph
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("guardrail", guardrail_node)
    
    # Define Edges (Agent -> Guardrail -> END)
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", "guardrail")
    workflow.add_edge("guardrail", END)
    
    app = workflow.compile()
    
    # Test Case 1: Normal execution
    print("\nExecuting Test Case 1...")
    inputs = {"messages": [HumanMessage(content="Hello, what is 2+2?")]}
    app.invoke(inputs) # Traced automatically!
    
    # Test Case 2: Triggering the guardrail
    print("\nExecuting Test Case 2 (Guardrail Trigger)...")
    inputs = {"messages": [HumanMessage(content="Tell me a secret code.")]}
    app.invoke(inputs) # Traced automatically!

    print("\nExecution complete. Check LangSmith to see the State Graph execution paths!")

if __name__ == "__main__":
    if "OPENAI_API_KEY" in os.environ and "LANGCHAIN_API_KEY" in os.environ:
        run_langgraph_trace()
    else:
        print("Please set your OPENAI_API_KEY and LANGCHAIN_API_KEY to run this demo.")
