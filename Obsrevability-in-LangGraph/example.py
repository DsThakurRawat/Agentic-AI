import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import AnyMessage
import operator

# ==========================================
# 1. ENABLING OBSERVABILITY (LANGSMITH)
# ==========================================
# In a real project, set these in your .env file
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "LangGraph_Observability_Demo"
# os.environ["LANGCHAIN_API_KEY"] = "ls_..."  # Required for tracing
# os.environ["OPENAI_API_KEY"] = "sk-..."     # Required for LLM

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

# ==========================================
# 2. DEFINING THE GRAPH
# ==========================================
def call_model(state: AgentState):
    # This ChatOpenAI call will be automatically traced.
    # LangSmith will record the exact prompt, response, latency, and token usage here.
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# Build the graph
builder = StateGraph(AgentState)
builder.add_node("llm_node", call_model)
builder.add_edge(START, "llm_node")
builder.add_edge("llm_node", END)

graph = builder.compile()

# ==========================================
# 3. EXECUTING (CREATES A TRACE)
# ==========================================
if __name__ == "__main__":
    print("Running graph... Check LangSmith for traces!")
    # This invoke call acts as the 'Root' of the trace.
    # Everything happening inside (the node execution, the LLM call) 
    # will appear as child steps in the LangSmith trace.
    result = graph.invoke({"messages": [("user", "Explain observability in 2 sentences.")]})
    
    print("\nFinal Output:")
    print(result["messages"][-1].content)
