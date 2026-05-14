import os
from langsmith import Client
from langchain_openai import ChatOpenAI
from langsmith.evaluation import evaluate

"""
Module 4: Agentic Frameworks & Production Features

Topic: Features of LangSmith - Datasets and Evaluations

This demo shows how to programmatically create a dataset in LangSmith 
and run an automated evaluation against it. This is a core feature for 
ensuring your LLM doesn't regress when you change prompts or models.
"""

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "LangSmith-Masterclass-Evals"

# Initialize the LangSmith client
client = Client()

def create_dataset_and_evaluate():
    print("1. Creating a Dataset in LangSmith...")
    dataset_name = "Agentic-Math-Dataset-Demo"
    
    # Check if dataset exists, if not create it
    if not client.has_dataset(dataset_name=dataset_name):
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="A simple dataset for evaluating math capabilities.",
        )
        # Add examples to the dataset
        client.create_examples(
            inputs=[
                {"question": "What is 2 + 2?"},
                {"question": "What is 10 / 2?"},
                {"question": "What is 3 * 3?"}
            ],
            outputs=[
                {"answer": "4"},
                {"answer": "5"},
                {"answer": "9"}
            ],
            dataset_id=dataset.id,
        )
        print("Dataset created successfully.")
    else:
        print("Dataset already exists.")

    print("\n2. Defining the Application Logic to Evaluate...")
    # This is the function we want to evaluate. It could be an Agent, a RAG chain, etc.
    def math_agent(inputs: dict) -> dict:
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        # Force the LLM to just output the number
        response = llm.invoke(f"Answer the math question with just the number. {inputs['question']}")
        return {"output": response.content}

    print("\n3. Defining Custom Evaluator...")
    # An evaluator function that checks if the model's output matches the expected output
    def exact_match_evaluator(run, example):
        # run.outputs contains our application's response
        # example.outputs contains the ground-truth from the dataset
        model_answer = run.outputs.get("output", "").strip()
        expected_answer = example.outputs.get("answer", "").strip()
        
        score = 1 if model_answer == expected_answer else 0
        return {"key": "exact_match", "score": score}

    print("\n4. Running the Evaluation...")
    # Run the evaluate function
    # This automatically fetches the dataset, runs the inputs through the math_agent,
    # and scores the outputs using exact_match_evaluator. The results are logged to LangSmith!
    experiment_results = evaluate(
        math_agent, # The logic to test
        data=dataset_name, # The dataset to test against
        evaluators=[exact_match_evaluator], # The scoring metrics
        experiment_prefix="math-eval-test",
    )
    
    print("\nEvaluation complete! Open LangSmith to view the Evaluation Dashboard.")

if __name__ == "__main__":
    if "OPENAI_API_KEY" in os.environ and "LANGCHAIN_API_KEY" in os.environ:
        create_dataset_and_evaluate()
    else:
        print("Please set your OPENAI_API_KEY and LANGCHAIN_API_KEY to run this demo.")
