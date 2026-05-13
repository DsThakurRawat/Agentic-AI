from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from state import AgentState
from tools import AVAILABLE_TOOLS
from nodes import reasoning_agent_node, reflection_node

# ============================================================================
# LANGGRAPH STARTER KIT: COMPILE WORKFLOW GRAPH
# ============================================================================
# Assembles state machine paths, registers execution nodes, attaches static
# checkpointer instances, and provides programmatic conditional routing blocks.

# --- 1. Define Conditional Edge Router Logic ---
def route_agent_actions(state: AgentState) -> Literal["tools", "reflection", "__end__"]:
    """
    Evaluates runtime outputs dynamically to direct downstream transition flows.
    Checks if the model generated functional tool invocations or output text directly.
    """
    messages = state.get("messages", [])
    if not messages:
        return "__end__"
        
    last_message = messages[-1]
    
    # Check if the LLM generated structured tool call array requests
    if getattr(last_message, "tool_calls", None):
        print(f"🔀 --- [ROUTER] Intercepted Tool Invocations -> Redirecting to Tools execution branch ---")
        return "tools"
        
    # Example auxiliary condition: Trigger reflection pass on specific depth cycles
    depth = state.get("iteration_depth", 0)
    if depth == 1:
        print("🔀 --- [ROUTER] Cycle validation limits met -> Redirecting to Reflection audit layer ---")
        return "reflection"
        
    print("🔀 --- [ROUTER] Terminal evaluation complete -> Proceeding cleanly to Workflow completion ---")
    return "__end__"

# --- 2. Build and Map Topologies ---
workflow = StateGraph(AgentState)

# Define native prebuilt Tool execution node wrapper
tool_node = ToolNode(tools=AVAILABLE_TOOLS)

# Register logical operational nodes
workflow.add_node("agent", reasoning_agent_node)
workflow.add_node("tools", tool_node)
workflow.add_node("reflection", reflection_node)

# Map edge transition arrays
workflow.add_edge(START, "agent")

# Map conditional divergence paths leading out of core agent blocks
workflow.add_conditional_edges(
    "agent",
    route_agent_actions,
    {
        "tools": "tools",
        "reflection": "reflection",
        "__end__": END
    }
)

# Loop paths back into the inference layer following tool execution or reflection passes
workflow.add_edge("tools", "agent")
workflow.add_edge("reflection", "agent")

# --- 3. Compile Runnable Application Instances ---
# Attach static ephemeral state persistence trackers
memory_checkpointer = MemorySaver()

# Compile primary runtime object compatible with LangGraph Studio interfaces
graph = workflow.compile(checkpointer=memory_checkpointer)

# --- 4. Local Execution Verification Entrypoint ---
if __name__ == "__main__":
    from langchain_core.messages import HumanMessage
    
    print("🚀 Booting modular LangGraph Starter Architecture Graph...")
    
    # Thread map keys required to track persistence blocks per user session
    config = {"configurable": {"thread_id": "starter_kit_demo_001"}}
    
    initial_input = {
        "messages": [HumanMessage(content="Search for info about CampusX and tell me current system time.")],
        "iteration_depth": 0,
        "current_agent": "system_bootstrap"
    }
    
    # Stream event iterations sequentially
    for output_event in graph.stream(initial_input, config=config):
        for node_id, output_payload in output_event.items():
            print(f"\n⚡ Stream response captured payload emitted from: '{node_id}'")
            messages_list = output_payload.get("messages", [])
            if messages_list:
                print(f"-> Output preview: {str(messages_list[-1].content)[:150]}...")

    print("\n✅ Stateful Modular Workflows Executed & Compiled Successfully.")
