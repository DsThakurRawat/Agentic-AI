import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS

"""
Module 3: Advanced Application Tracing

Topic: Tracing a RAG App and Testing Queries

Retrieval-Augmented Generation (RAG) tracing is critical because failures usually happen
in the retrieval step, not the LLM generation step. LangSmith allows you to see exactly
what documents were retrieved for a specific query.
"""

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "LangSmith-Masterclass-RAG"

def setup_mock_vectorstore():
    """Sets up a simple in-memory vector store for the demo."""
    texts = [
        "LangSmith is a platform for tracing and evaluating LLMs.",
        "LangGraph is a library for building stateful, multi-actor applications with LLMs.",
        "FAISS is a library for efficient similarity search and clustering of dense vectors."
    ]
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts, embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 2})

def run_rag_trace():
    print("Setting up RAG pipeline...")
    retriever = setup_mock_vectorstore()
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    template = """Answer the question based ONLY on the following context:
    {context}
    
    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    
    # Create the RAG Chain
    # We use RunnablePassthrough to pass the question down the chain, while
    # assigning the 'context' variable by running the retriever.
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    question = "What is the difference between LangSmith and LangGraph?"
    print(f"Asking: '{question}'")
    
    # When this executes, LangSmith will show:
    # 1. The exact embedding generation for the question
    # 2. The top-k documents returned by FAISS (Crucial for debugging 'Testing Query')
    # 3. The final prompt with the injected context
    # 4. The LLM generation
    response = rag_chain.invoke(question)
    
    print("\nAnswer:")
    print(response)

if __name__ == "__main__":
    if "OPENAI_API_KEY" in os.environ and "LANGCHAIN_API_KEY" in os.environ:
        run_rag_trace()
    else:
        print("Please set your OPENAI_API_KEY and LANGCHAIN_API_KEY to run this demo.")
