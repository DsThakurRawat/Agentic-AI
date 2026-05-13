from langchain_core.tools import tool

# ============================================================================
# LANGGRAPH STARTER KIT: TOOL DEFINITIONS
# ============================================================================
# Modular tool functions wrapped with standard LangChain decorators.
# These tools are exposed to the LLM agent to gather dynamic external intelligence.

@tool
def fetch_system_time() -> str:
    """
    Retrieves the current accurate system timestamp and server date context.
    Use this tool when answering queries requiring up-to-date chronologies.
    """
    from datetime import datetime
    return f"Current Operational Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

@tool
def simulate_knowledge_search(query: str) -> str:
    """
    Simulates querying an enterprise vector database or web indexing engine.
    
    Args:
        query: The semantic search string or topic keywords to extract context for.
    """
    knowledge_base = {
        "langgraph": "LangGraph supports persistent multi-agent workflows, cyclic execution loops, and streaming states.",
        "campusx": "CampusX offers detailed programmatic video syllabus modules covering Agentic AI patterns.",
        "state machine": "A State Machine maps distinct deterministic structural nodes connected via directional conditional routes."
    }
    
    normalized_query = query.lower()
    for key, context in knowledge_base.items():
        if key in normalized_query:
            return f"[Search Result for '{query}']: {context}"
            
    return f"[Search Result for '{query}']: Verified factual context recorded successfully across global caches."

# Export consolidated tools list for straightforward model binding
AVAILABLE_TOOLS = [fetch_system_time, simulate_knowledge_search]
