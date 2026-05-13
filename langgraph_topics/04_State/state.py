"""
State Schema Contracts & Value Override Semantics Demonstration
Implements two heavy functional examples showcasing TypedDict direct value replacement and Pydantic validation mapping.
"""

from typing import TypedDict, Optional
from pydantic import BaseModel, Field, ValidationError
from langgraph.graph import StateGraph, START, END


# ============================================================================
# EXAMPLE 1: Pure TypedDict Master Schema demonstrating Override Semantics
# ============================================================================

class OverrideStateSchema(TypedDict):
    """Data interface tracking persistent context keys across transformation nodes."""
    target_host: str
    active_connections: int
    system_log: Optional[str]


def pre_processing_step(state: OverrideStateSchema) -> dict:
    """Modifies scalar keys demonstrating subset dictionary return replacement."""
    host = state["target_host"]
    print(f"[Node 1] Scanning base payload configurations targeting host: '{host}'")
    
    # Return subset overriding active_connections base key only
    return {"active_connections": state["active_connections"] + 5}


def final_audit_step(state: OverrideStateSchema) -> dict:
    """Overrides final log strings leaving unlisted keys untouched."""
    print(f"[Node 2] Polling shared graph state variable: Active Connections={state['active_connections']}")
    
    log_update = f"Host connection pool state evaluated successfully."
    return {"system_log": log_update}


def run_example_one():
    """Compiles state pipeline frameworks tracking subset overriding mechanisms."""
    print(f"\n{'='*70}\nEXAMPLE 1: Pure TypedDict State Override Flow\n{'='*70}")
    
    graph = StateGraph(OverrideStateSchema)
    graph.add_node("process", pre_processing_step)
    graph.add_node("audit", final_audit_step)
    
    graph.add_edge(START, "process")
    graph.add_edge("process", "audit")
    graph.add_edge("audit", END)
    
    app = graph.compile()
    
    initial_payload: OverrideStateSchema = {
        "target_host": "production-cluster-aws.us-east-1",
        "active_connections": 10,
        "system_log": None
    }
    
    print(f"Inbound Trigger Payload:\n{initial_payload}\n")
    final_output = app.invoke(initial_payload)
    print(f"\nCompleted Executable Graph State Output:\n{final_output}")


# ============================================================================
# EXAMPLE 2: High-Density Pydantic Validated State Schema Enforcement
# ============================================================================

class PydanticSecurityPayload(BaseModel):
    """Pydantic BaseModel structure enforcing rigid constraints against updates."""
    authorized_user: str = Field(..., min_length=3)
    security_clearance_tier: int = Field(1, ge=1, le=5)
    audit_trace: str = Field(...)


def security_scanner_node(state: dict) -> dict:
    """Attempts processing updates mapping strict Pydantic model validation layers."""
    print("[Security Node] Attempting validation update execution...")
    
    try:
        # Validate data constraints natively using BaseModel instantiation check
        validated_data = PydanticSecurityPayload(
            authorized_user=state["authorized_user"],
            security_clearance_tier=state["security_clearance_tier"] + 2,
            audit_trace="Tier Level Elevated"
        )
        print("  [Validation Gateway] Pydantic verification suite checks PASSED cleanly.")
        return validated_data.model_dump()
        
    except ValidationError as e:
        print(f"  [Validation Gateway Exception] Destructive payload parameters trapped:\n{e}")
        return {"audit_trace": "Validation Error Clobbered"}


def run_example_two():
    """Demonstrates high-density schema structure validation mappings."""
    print(f"\n{'='*70}\nEXAMPLE 2: Pydantic Validation Payload Enforcement Flow\n{'='*70}")
    
    # Simulating simple linear compilation wrapper
    test_scenarios = [
        {"authorized_user": "DevOps_Eng", "security_clearance_tier": 2, "audit_trace": "Init"},
        {"authorized_user": "QA", "security_clearance_tier": 5, "audit_trace": "Init"} # Tier > 5 violates bounds
    ]
    
    for idx, ts in enumerate(test_scenarios, 1):
        print(f"\n--- Injecting Candidate Payload Sequence #{idx} ---")
        output = security_scanner_node(ts)
        print(f"Resulting Local Dictionary Update State: {output['audit_trace']}")


if __name__ == "__main__":
    run_example_one()
    run_example_two()
