# Module 4: State (Schema Contracts & Value Override Semantics)

The central communication mechanism in LangGraph is its **Shared Graph State**. Instead of isolated memory models, functional nodes read from and return subset overrides directly onto a structured, persistent state dictionary instance.

---

## 📑 Schema Contracts & Structural Validation

To prevent malformed data from causing downstream processing exceptions, state structures must enforce explicit data contracts. Developers author these typing schemas natively using two primary standards:

### 1. Pure Python `TypedDict` Definitions
Standard dict structural wrappers. Highly lightweight, fast serialization overhead, best suited for basic mathematical or string aggregation flows.

### 2. High-Density Pydantic Validated Schemas
Enforces strict dynamic programmatic validation rules during instantiation runs (e.g., matching input string formats, regex validation, numerical bounds checking).

---

## ⚡ Master State Dictionary Override Semantics

> [!IMPORTANT]
> A node **does not** mutate the shared master graph state object directly in memory. It computes and returns a localized dictionary subset. The framework engine extracts these returned key-value updates to overwrite targeted base keys inside the persistent execution thread.

### Value Replacement Rules
* **Keys Present in Return Dictionary**: The engine overwrites the matching existing master graph key directly with the new payload value returned by the active node.
* **Keys Omitted from Return Dictionary**: Retain their baseline status across the execution turn smoothly.

```mermaid
graph TD
    subgraph Master Persistent State Dictionary
        A[session_user: 'Admin']
        B[token_bucket: 15]
        C[action_log: 'Login Verified']
    end

    subgraph Node Operation Block
        N[Returns: {'token_bucket': 20, 'action_log': 'Executed Job'}]
    end

    subgraph Serialized Superstep Output
        A2[session_user: 'Admin' - Unchanged Base State]
        B2[token_bucket: 20 - Overridden]
        C2[action_log: 'Executed Job' - Overridden]
    end

    A --> N
    B --> N
    C --> N
    N --> A2
    N --> B2
    N --> C2
```

---

## 💻 Technical Implementations Covered

The accompanying `state.py` module implements two complete functional scenarios showcasing typing integration:
* **Example 1**: Implements a standard **`TypedDict` Master Schema** tracking scalar key updates across discrete pipeline processing steps to prove explicit dictionary key replacement semantics.
* **Example 2**: Implements a **Pydantic Validation Framework Architecture** ensuring strict bounds validation checking against critical payload updates during live computational processing cycles.
