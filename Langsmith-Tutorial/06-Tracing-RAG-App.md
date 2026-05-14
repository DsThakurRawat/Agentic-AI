# Tracing RAG Apps (Theory & Visualization)

This document accompanies `06_tracing_rag_app.py`.

## Theory: Debugging Retrieval

Retrieval-Augmented Generation (RAG) pipelines consist of two distinct failure points:
1. **Retrieval Failure:** The vector database returned irrelevant documents.
2. **Generation Failure:** The LLM ignored the relevant documents and hallucinated.

Without observability, a bad response is a black box. LangSmith breaks the trace down so you can explicitly test the query and see *exactly* what context was provided to the LLM.

## Visualization: RAG Trace Pipeline

Below is how a typical RAG invocation is visualized in LangSmith. Notice how the parallel execution of the `Retriever` and the `RunnablePassthrough` (passing the question) merge into the prompt.

```mermaid
graph TD
    Input[User Query: "What is LangSmith?"] --> Parallel{Parallel Execution}
    
    Parallel --> R[Retriever: FAISS]
    R --> E[Embeddings API]
    E --> Docs[Returned Top-K Documents]
    
    Parallel --> PT[RunnablePassthrough]
    PT --> Q[Question string]
    
    Docs --> Prompt[Prompt Formatting]
    Q --> Prompt
    
    Prompt --> LLM[ChatOpenAI Generation]
    LLM --> Output[Final Output String]
    
    style R fill:#e3f2fd,stroke:#1976d2
    style LLM fill:#fff3e0,stroke:#f57c00
    style Prompt fill:#f1f8e9,stroke:#689f38
```

### Testing Queries in LangSmith
If the final output is wrong, you click on the **Retriever** node in the LangSmith UI. If the `Top-K Documents` do not contain the answer, your prompt/LLM is fine—you need to fix your chunking, embedding model, or search logic!
