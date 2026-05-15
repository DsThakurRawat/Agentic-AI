import os
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from langchain_core.tools import tool, BaseTool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import operator

# ==========================================
# 1. TOOL TYPE A: Simple @tool decorator
# ==========================================
@tool
def get_system_time() -> str:
    """
    Returns the current server time. 
    Use this tool whenever the user asks for the current time or date.
    """
    from datetime import datetime
    return f"The current time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# ==========================================
# 2. TOOL TYPE B: @tool with Pydantic Schema
# ==========================================
class UserLookupInput(BaseModel):
    user_id: int = Field(description="The unique integer ID of the user.")
    detailed: bool = Field(default=False, description="Whether to fetch detailed info or just the basics.")

@tool(args_schema=UserLookupInput)
def fetch_user_data(user_id: int, detailed: bool = False) -> str:
    """
    Fetches the profile data for a specific user from the database.
    """
    # Simulated database
    db = {
        101: {"name": "Alice", "role": "Admin", "email": "alice@company.com"},
        102: {"name": "Bob", "role": "User", "email": "bob@company.com"}
    }
    
    user = db.get(user_id)
    if not user:
        return f"Error: User with ID {user_id} not found."
        
    if detailed:
        return str(user)
    else:
        return f"User {user['name']} is a {user['role']}."

# ==========================================
# 3. TOOL TYPE C: Subclassing BaseTool
# ==========================================
class CalculatorInput(BaseModel):
    a: float = Field(description="First number")
    b: float = Field(description="Second number")
    operation: Literal["add", "subtract", "multiply", "divide"] = Field(
        description="The math operation to perform."
    )

class MathTool(BaseTool):
    name: str = "math_calculator"
    description: str = "A precise calculator for math operations. Use this instead of trying to do math in your head."
    args_schema: type[BaseModel] = CalculatorInput

    def _run(self, a: float, b: float, operation: str) -> str:
        try:
            if operation == "add": return str(a + b)
            if operation == "subtract": return str(a - b)
            if operation == "multiply": return str(a * b)
            if operation == "divide": return str(a / b)
        except ZeroDivisionError:
            return "Error: Division by zero is not allowed."
        return "Error: Invalid operation."

# ==========================================
# 4. BUILDING THE LANGGRAPH WITH TOOLS
# ==========================================

# Combine all our tools into a list
tools = [get_system_time, fetch_user_data, MathTool()]

# Define the State
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

# Define the LLM and bind the tools to it
# Note: You need OPENAI_API_KEY set in your environment
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
llm_with_tools = llm.bind_tools(tools)

# Node: Agent calling the LLM
def agent_node(state: AgentState):
    # Pass the message history to the LLM
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# Node: Tool execution node provided by LangGraph
# ToolNode automatically reads the ToolCall from the LLM response,
# executes the matching tool, and returns a ToolMessage.
tool_node = ToolNode(tools)

# Build the Graph
builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)

# Control Flow Edges
builder.add_edge(START, "agent")

# 'tools_condition' automatically routes to 'tools' if the LLM made a tool call, 
# otherwise it routes to END.
builder.add_conditional_edges(
    "agent",
    tools_condition,
)

# After tools run, go back to the agent so it can read the tool output and respond
builder.add_edge("tools", "agent")

# Compile
graph = builder.compile()

# ==========================================
# 5. EXECUTION EXAMPLE
# ==========================================
if __name__ == "__main__":
    print("--- Example 1: Basic Tool (System Time) ---")
    inputs = {"messages": [("user", "What time is it right now?")]}
    result = graph.invoke(inputs)
    print("Final Response:", result["messages"][-1].content)
    print("\n" + "="*50 + "\n")

    print("--- Example 2: Pydantic Tool (User Lookup) ---")
    inputs = {"messages": [("user", "Can you look up user ID 101 and give me detailed info?")]}
    result = graph.invoke(inputs)
    print("Final Response:", result["messages"][-1].content)
    print("\n" + "="*50 + "\n")
    
    print("--- Example 3: Subclassed Tool (Math) ---")
    inputs = {"messages": [("user", "What is 1234 multiplied by 5678?")]}
    result = graph.invoke(inputs)
    print("Final Response:", result["messages"][-1].content)
