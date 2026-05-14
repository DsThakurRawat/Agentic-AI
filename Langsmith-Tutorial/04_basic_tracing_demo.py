import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

"""
Module 2: Applied Code Demonstrations - Basic Setup & Tracing

Topic: Setting up the environment and tracing a standard LLM call.

To enable LangSmith tracing, you strictly need these environment variables:
1. LANGCHAIN_TRACING_V2=true
2. LANGCHAIN_API_KEY=<your_api_key>
3. LANGCHAIN_PROJECT=<your_project_name> (defaults to "default")

Once these are set, any LangChain components you use will automatically 
log their inputs, outputs, latency, and token usage to LangSmith.
"""

# Hardcoding for demonstration purposes, but usually loaded via python-dotenv (.env)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_API_KEY"] = "ls_..." 
os.environ["LANGCHAIN_PROJECT"] = "LangSmith-Masterclass-Demo"
# os.environ["OPENAI_API_KEY"] = "sk-..." 

def run_basic_trace():
    print("Initializing Model and Prompt...")
    # 1. Initialize the Model
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

    # 2. Create a Prompt Template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant who always replies in pirate speak."),
        ("user", "{input}")
    ])

    # 3. Create the Chain (Prompt -> LLM -> Output Parser)
    chain = prompt | llm | StrOutputParser()

    print("Invoking chain... (This will automatically be traced in LangSmith)")
    
    # 4. Invoke the chain
    # In LangSmith, you will see a single trace containing 3 child runs:
    # - ChatPromptTemplate formatting
    # - ChatOpenAI execution (with exact token usage and latency)
    # - StrOutputParser parsing
    response = chain.invoke({"input": "Explain what LangSmith is in one sentence."})
    
    print("\nResponse:")
    print(response)

if __name__ == "__main__":
    # Ensure API keys are present before running
    if "OPENAI_API_KEY" in os.environ and "LANGCHAIN_API_KEY" in os.environ:
        run_basic_trace()
    else:
        print("Please set your OPENAI_API_KEY and LANGCHAIN_API_KEY to run this demo.")
