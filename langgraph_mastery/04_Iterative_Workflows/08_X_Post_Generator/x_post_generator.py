"""
Production Cyclical Social Content Generator Engine
Translates `8_X_post_generator.ipynb` demonstrating self-correction loops and audit history reducers.
"""

import os
import operator
from typing import TypedDict, Literal, Annotated, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END


# 1. Define Structured Critic Gatekeeper Schema
class TweetEvaluation(BaseModel):
    """Pydantic definition ensuring strict criticism formats."""
    evaluation: Literal["approved", "needs_improvement"] = Field(
        description="Binary consensus evaluation flag"
    )
    feedback: str = Field(
        description="Detailed actionable critique explaining strengths and deficiencies"
    )


# 2. Define Shared State Interface leveraging Reducers
class TweetState(TypedDict):
    """
    State container leveraging custom list reducers.
    'operator.add' appends generated posts and feedbacks to their respective historical arrays.
    """
    topic: str
    tweet: Optional[str]
    evaluation: Optional[Literal["approved", "needs_improvement"]]
    feedback: Optional[str]
    iteration: int
    max_iteration: int
    
    tweet_history: Annotated[list[str], operator.add]
    feedback_history: Annotated[list[str], operator.add]


# 3. Define Core Workflow Nodes
def generate_tweet_node(state: TweetState) -> dict:
    """Invokes generator LLMs authoring highly engaging meme-logic content."""
    load_dotenv()
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    topic = state["topic"]
    print(f"\n[Generation Phase] Authoring original viral post for topic: '{topic}'...")
    
    messages = [
        SystemMessage(content="You are a brilliant, witty, and highly relatable Twitter/X influencer."),
        HumanMessage(content=(
            f"Write a short, original, and punchy tweet on the topic: '{topic}'.\n\n"
            f"Rules:\n"
            f"- Strictly NO question-answer format.\n"
            f"- Maximum 280 characters limit.\n"
            f"- Rely on clever observational humor, meme logic, or sharp irony.\n"
            f"- Keep language simple, accessible, and highly shareable."
        ))
    ]
    
    response_text = model.invoke(messages).content
    print(f"  Draft Generated:\n  {response_text}")
    return {"tweet": response_text, "tweet_history": [response_text]}


def evaluate_tweet_node(state: TweetState) -> dict:
    """Invokes structured output evaluators guarding quality bounds."""
    load_dotenv()
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.0).with_structured_output(TweetEvaluation)
    
    tweet = state["tweet"]
    print("[Evaluation Phase] Analyzing virality, humor depth, and formatting criteria...")
    
    messages = [
        SystemMessage(
            content="You are a strict, objective social media viral architect. You evaluate content against formatting bounds and humor depth."
        ),
        HumanMessage(content=(
            f"Evaluate the viral viability and formatting bounds of this candidate post:\n\n"
            f"'{tweet}'\n\n"
            f"Evaluation Criteria:\n"
            f"1. Originality: Avoid stale paradigms.\n"
            f"2. Humor Depth: Genuinely clever framing.\n"
            f"3. Formatting constraints: Must avoid Q&A setup styles and stay within 280 characters limit.\n\n"
            f"Respond using structured fields mapping evaluation and feedback."
        ))
    ]
    
    output: TweetEvaluation = model.invoke(messages)
    print(f"  Consensus Target: {output.evaluation.upper()}")
    return {
        "evaluation": output.evaluation,
        "feedback": output.feedback,
        "feedback_history": [output.feedback]
    }


def optimize_tweet_node(state: TweetState) -> dict:
    """Refines candidate texts leveraging specific actionable critiques."""
    load_dotenv()
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    
    current_iter = state["iteration"]
    print(f"[Optimization Loop: Attempt #{current_iter}] Re-authoring based on feedback critique...")
    
    messages = [
        SystemMessage(content="You optimize and polish draft social content based on reviewer critiques."),
        HumanMessage(content=(
            f"Refine this draft post based on the attached reviewer critique:\n\n"
            f"Feedback Critique:\n'{state['feedback']}'\n\n"
            f"Original Topic: '{state['topic']}'\n"
            f"Current Draft Text:\n'{state['tweet']}'\n\n"
            f"Re-write it to resolve all listed deficiencies while maintaining punchiness."
        ))
    ]
    
    optimized_text = model.invoke(messages).content
    print(f"  Optimized Output:\n  {optimized_text}")
    return {
        "tweet": optimized_text,
        "iteration": current_iter + 1,
        "tweet_history": [optimized_text]
    }


def route_evaluation_switch(state: TweetState) -> Literal["approved", "needs_improvement"]:
    """Conditional router loop steering execution paths."""
    if state["evaluation"] == "approved" or state["iteration"] >= state["max_iteration"]:
        return "approved"
    else:
        return "needs_improvement"


# 4. Compile Cyclical Topologies
def compile_content_generator():
    """Assembles nodes, standard edges, and loop routing loops."""
    graph = StateGraph(TweetState)
    
    graph.add_node("generate", generate_tweet_node)
    graph.add_node("evaluate", evaluate_tweet_node)
    graph.add_node("optimize", optimize_tweet_node)
    
    graph.add_edge(START, "generate")
    graph.add_edge("generate", "evaluate")
    
    # Register conditional loop router
    graph.add_conditional_edges(
        "evaluate",
        route_evaluation_switch,
        {"approved": END, "needs_improvement": "optimize"}
    )
    
    graph.add_edge("optimize", "evaluate")
    
    return graph.compile()


if __name__ == "__main__":
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("[CAUTION] OPENAI_API_KEY missing from environment configuration.")
        
    workflow = compile_content_generator()
    
    initial_payload: TweetState = {
        "topic": "Debugging multi-agent systems at 2 AM",
        "tweet": None,
        "evaluation": None,
        "feedback": None,
        "iteration": 1,
        "max_iteration": 4,
        "tweet_history": [],
        "feedback_history": []
    }
    
    print("--- Initializing Cyclical Content Generator Loop ---")
    try:
        final_state = workflow.invoke(initial_payload)
        
        print("\n" + "="*60)
        print("FINAL RESOLVED POST PAYLOAD")
        print("="*60)
        print(final_state["tweet"])
        
        print("\n" + "-"*60)
        print("GENERATION ATTEMPT AUDIT HISTORY:")
        print("-"*60)
        for idx, item in enumerate(final_state["tweet_history"], 1):
            print(f"Attempt #{idx}:\n{item}\n")
            
    except Exception as e:
        print(f"Engine execution error: {e}")
