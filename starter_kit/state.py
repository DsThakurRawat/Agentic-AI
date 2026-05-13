import operator
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage

# ============================================================================
# LANGGRAPH STARTER KIT: STATE SCHEMA DEFINITIONS
# ============================================================================
# The central state buffer schema shared across all nodes and edges.
# Built-in reducer operators manage message array aggregation and state mutations.

class AgentState(TypedDict):
    """
    Core state dictionary maintaining full dialogue context and runtime tracking parameters.
    
    Attributes:
        messages: Accumulated sequence of Human, AI, System, and Tool messages.
                  Uses `operator.add` reducer to append new items to the global state list.
        current_agent: Identifies the active agent routing scope.
        iteration_depth: Tracks cyclic execution counts to prevent unbounded loops.
    """
    messages: Annotated[list[BaseMessage], operator.add]
    current_agent: str
    iteration_depth: int
