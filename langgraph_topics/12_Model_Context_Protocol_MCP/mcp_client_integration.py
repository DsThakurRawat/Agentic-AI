"""
Module 12: Model Context Protocol (MCP) Client Integration
==========================================================

Demonstrates how to connect a LangGraph agent to multiple MCP servers
using stdio and sse transports to access standardized tools.
"""

import asyncio
import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient

# ============================================================================
# 1. MCP CLIENT INITIALIZATION
# ============================================================================

# The MultiServerMCPClient allows one agent to talk to many tool servers.
# It abstracts the communication (stdio/sse) into standard LangChain tools.
client = MultiServerMCPClient(
    {
        "math_service": {
            "transport": "stdio",
            "command": "python3",
            "args": ["path/to/math_server.py"],  # Point to your local MCP server
        },
        "enterprise_api": {
            "transport": "streamable_http",
            "url": "https://api.example.com/mcp"
        }
    }
)


class MCPChatState(TypedDict):
    """
    State tracking messages with cumulative list reduction.
    """
    messages: Annotated[list[BaseMessage], add_messages]


# ============================================================================
# 2. BUILDING THE MCP-ENABLED GRAPH
# ============================================================================

async def build_mcp_graph():
    """
    Asynchronously fetches tools from MCP servers and builds the graph.
    """
    print("[MCP Client] Fetching tool definitions from remote servers...")
    
    # Dynamically discover all tools exposed by the configured servers
    tools = await client.get_tools()
    
    llm = ChatOpenAI(model="gpt-4o")
    llm_with_tools = llm.bind_tools(tools)

    # Main inference node
    async def call_model_node(state: MCPChatState):
        response = await llm_with_tools.ainvoke(state["messages"])
        return {"messages": [response]}

    # Automated execution hub for the discovered MCP tools
    tool_node = ToolNode(tools)

    # Graph Topology
    workflow = StateGraph(MCPChatState)
    workflow.add_node("agent", call_model_node)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")

    return workflow.compile()


async def run_mcp_demo():
    """
    Executes a test query requiring MCP tool interaction.
    """
    print(f"\n{'='*75}\nMODULE 12: Model Context Protocol (MCP) Integration\n{'='*75}")
    
    agent = await build_mcp_graph()
    
    print("\n[User Query] Calculating complex expenses via Math MCP Server...")
    query = {"messages": [HumanMessage(content="Calculate the sum of 450.5 and 1290.75 using the math server.")]}
    
    # Invoke the agent asynchronously
    # result = await agent.ainvoke(query)
    # print(f"\nFinal Response:\n  {result['messages'][-1].content}")
    print("\nDemo Note: This requires active MCP servers to be running.")


if __name__ == "__main__":
    asyncio.run(run_mcp_demo())
