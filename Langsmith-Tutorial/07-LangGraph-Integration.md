# LangGraph Integration (Theory & Visualization)

This document accompanies `07_langgraph_integration.py`.

## Theory: Tracing State Machines

LangGraph utilizes cyclical graphs (state machines) rather than linear chains. An agent might think, call a tool, evaluate the tool, realize it made a mistake, and call another tool. 

LangSmith natively understands LangGraph's `StateGraph`. When an application loops, LangSmith groups those loops logically.

## Visualization: StateGraph and Execution Trace

### 1. The Application Graph Structure
This is the physical layout of the agent we built in Python:

```mermaid
stateDiagram-v2
    [*] --> AgentNode
    AgentNode --> GuardrailNode
    GuardrailNode --> [*] : If safe
    GuardrailNode --> AgentNode : (In advanced setups, it loops back)
```

### 2. The LangSmith Trace Output
When the graph executes, LangSmith creates a trace that groups executions by graph steps. In our demo (where the guardrail was triggered), the trace looks like this:

```mermaid
graph TD
    App[Compiled LangGraph App] --> S1[Step 1: agent_node]
    S1 --> LLM[ChatOpenAI Call]
    
    App --> S2[Step 2: guardrail_node]
    S2 --> Override[Message Override Logic]
    
    style App fill:#eceff1,stroke:#607d8b
    style S1 fill:#e8eaf6,stroke:#3f51b5
    style S2 fill:#ffebee,stroke:#d32f2f
```

### Why LangGraph Needs LangSmith
If an agent gets stuck in an infinite loop, looking at standard terminal logs is a nightmare. LangSmith allows you to click on `Step 45` of a loop, see exactly what the agent's state was at that exact moment, and understand why it decided to loop again.
