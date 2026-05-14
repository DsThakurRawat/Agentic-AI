import os
from langsmith import traceable
from langchain_openai import ChatOpenAI

"""
Module 2: Applied Code Demonstrations - Instrumenting Custom Functions

Topic: What if you aren't using LangChain components? 
LangSmith can trace ANY Python code using the `@traceable` decorator.

This is highly relevant when building custom Agentic workflows where 
you might write custom API calls, complex math functions, or database 
lookups that you want to show up in the LangSmith trace tree.
"""

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "LangSmith-Masterclass-Demo"

# The @traceable decorator tells LangSmith to record the inputs and outputs of this specific function.
@traceable(run_type="tool", name="Database Lookup Tool")
def mock_database_lookup(user_id: int) -> str:
    """Simulates a database lookup that we want tracked in LangSmith."""
    print(f"Looking up user {user_id}...")
    # Simulate some logic
    if user_id == 101:
        return "Alice - Premium Tier"
    return "Unknown User"

@traceable(run_type="llm", name="Generate Custom Greeting")
def generate_greeting(user_info: str) -> str:
    """A custom function that calls an LLM, but is traced as a single block."""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    response = llm.invoke(f"Write a 1 sentence welcome message for this user profile: {user_info}")
    return response.content

@traceable(run_type="chain", name="Main Agent Workflow")
def main_workflow(user_id: int):
    """
    This is the parent function. Because it is traceable, and it calls other 
    traceable functions, LangSmith will automatically build a nested tree:
    
    Main Agent Workflow
    ├── Database Lookup Tool
    └── Generate Custom Greeting
         └── ChatOpenAI (automatically traced because we use the LangChain object)
    """
    print(f"Starting workflow for ID: {user_id}")
    
    # Step 1: Tool call
    user_info = mock_database_lookup(user_id)
    
    # Step 2: LLM call
    greeting = generate_greeting(user_info)
    
    print("\nFinal Result:")
    print(greeting)
    return greeting

if __name__ == "__main__":
    if "OPENAI_API_KEY" in os.environ and "LANGCHAIN_API_KEY" in os.environ:
        main_workflow(101)
    else:
        print("Please set your OPENAI_API_KEY and LANGCHAIN_API_KEY to run this demo.")
