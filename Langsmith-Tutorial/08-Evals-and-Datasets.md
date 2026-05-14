# Evaluations and Datasets (Theory & Visualization)

This document accompanies `08_evals_and_datasets.py`.

## Theory: The Evaluation Loop

In traditional software, you write unit tests (`assert 2 + 2 == 4`). In Generative AI, outputs are non-deterministic, so you use **Evaluations (Evals)**. 

LangSmith makes this process seamless by allowing you to:
1. Curate a **Dataset** (a collection of inputs and expected outputs).
2. Define a **Target** (your agent, RAG chain, or LLM function).
3. Define an **Evaluator** (a scoring function, often another LLM acting as a judge).
4. Run an **Experiment** which processes the dataset and logs the aggregate scores.

## Visualization: The Evaluation Architecture

Below is a visualization of what happens when you call the `evaluate()` function in LangSmith.

```mermaid
sequenceDiagram
    participant User/CI as Developer / CI Pipeline
    participant LS as LangSmith (Dataset)
    participant App as Target Agent/App
    participant Eval as Evaluator (e.g., Exact Match)

    User/CI->>LS: Start Experiment (`evaluate()`)
    LS->>App: Inject Input 1 (e.g., "What is 2+2?")
    App-->>LS: Output 1 ("4")
    
    LS->>Eval: Compare App Output ("4") with Expected ("4")
    Eval-->>LS: Score (1.0)
    
    LS->>App: Inject Input 2 (e.g., "What is 10/2?")
    App-->>LS: Output 2 ("5")
    
    LS->>Eval: Compare App Output ("5") with Expected ("5")
    Eval-->>LS: Score (1.0)
    
    LS-->>User/CI: Return Aggregate Experiment Results
```

### CI/CD Integration
The ultimate goal of this setup is to integrate it into GitHub Actions. If a pull request modifies an agent prompt, an automated action runs the LangSmith Evaluation. If the aggregate score drops below 90%, the pull request is blocked. This is how you confidently ship Agentic AI to production.
