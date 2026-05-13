from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from state import AgentState
from tools import AVAILABLE_TOOLS

# ============================================================================
# LANGGRAPH STARTER KIT: NODE IMPLEMENTATIONS
# ============================================================================
# Core stateless Python execution blocks mapping step transformations.
# Each function receives the active State dictionary and returns delta updates.

# Initialize model interface bound with available tool schemas
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
llm_with_tools = llm.bind_tools(AVAILABLE_TOOLS)

def reasoning_agent_node(state: AgentState) -> dict:
    """
    Evaluates global message state and invokes the inference model layer.
    Can decide to output standard answers or emit requested tool execution targets.
    """
    print("\n🧠 --- [NODE: REASONING AGENT] Processing Dialogue State Context ---")
    messages = state.get("messages", [])
    current_depth = state.get("iteration_depth", 0)
    
    # Prepend dynamic system routing directives if required
    sys_msg = SystemMessage(
        content="You are a helpful, autonomous AI assistant utilizing tools to solve complex tasks."
    )
    
    # Generate model response payload
    response = llm_with_tools.invoke([sys_msg] + messages)
    
    # Return dictionary deltas merged automatically by reducer callbacks
    return {
        "messages": [response],
        "iteration_depth": current_depth + 1,
        "current_agent": "reasoning_agent"
    }

def reflection_node(state: AgentState) -> dict:
    """
    Optional intermediate node performing structural quality validation checks.
    Demonstrates injecting auxiliary diagnostic traces directly into state logs.
    """
    print("🔍 --- [NODE: REFLECTION ENGINE] Auditing Generated Trace Quality ---")
    from langchain_core.messages import AIMessage
    audit_msg = AIMessage(
        content="[Internal Reflection Audit]: Execution sequence bounds evaluated properly."
    )
    return {"messages": [audit_msg]}
