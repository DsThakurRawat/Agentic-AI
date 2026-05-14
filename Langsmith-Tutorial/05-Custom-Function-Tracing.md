# Custom Function Tracing (Theory & Visualization)

This document accompanies `05_custom_function_tracing.py`.

## Theory: The `@traceable` Decorator

LangChain components automatically log to LangSmith, but production Agentic AI relies heavily on custom Python code (API calls, data processing, business logic). LangSmith solves this with the `@traceable` decorator.

By adding `@traceable(run_type="tool")` to any python function, LangSmith captures its inputs and outputs, and nests it perfectly within the active trace tree.

## Visualization: Nested Execution Graph

When `main_workflow()` is executed, LangSmith dynamically builds the following execution tree, treating your custom python functions exactly like LangChain objects.

```mermaid
graph TD
    A[Chain: main_workflow<br/>(Root Function)] --> B[Tool: Database Lookup Tool<br/>Input: id=101<br/>Output: 'Alice']
    A --> C[LLM: Generate Custom Greeting]
    C --> D[ChatOpenAI<br/>(Auto-traced LangChain object)]
    
    style A fill:#e8eaf6,stroke:#3f51b5
    style B fill:#ffebee,stroke:#d32f2f
    style C fill:#e8f5e9,stroke:#388e3c
    style D fill:#fff3e0,stroke:#f57c00
```

### Why is this important?
If `Generate Custom Greeting` fails or returns a weird response, you can immediately look at the `Database Lookup Tool` step in LangSmith to see if it passed bad data (e.g., passing `"Unknown User"` instead of `"Alice"`). This isolates bugs instantly.
