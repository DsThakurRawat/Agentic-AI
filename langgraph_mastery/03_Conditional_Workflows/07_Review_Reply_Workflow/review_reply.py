"""
Production Contextual Support Routing Automation
Translates `7_review_reply_workflow.ipynb` demonstrating dual structured validators and conditional routing.
"""

import os
from typing import TypedDict, Literal, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END


# 1. Define Multi-Schema Pydantic Output Definitions
class SentimentSchema(BaseModel):
    """Pydantic interface verifying strict initial sentiment labels."""
    sentiment: Literal["positive", "negative"] = Field(description="Derived sentiment orientation")


class DiagnosisSchema(BaseModel):
    """Pydantic interface extracting actionable metadata from negative feedback."""
    issue_type: Literal["UX", "Performance", "Bug", "Support", "Other"] = Field(
        description="Core technical classification domain"
    )
    tone: Literal["angry", "frustrated", "disappointed", "calm"] = Field(
        description="Identified emotional posture"
    )
    urgency: Literal["low", "medium", "high"] = Field(
        description="Perceived operational urgency factor"
    )


# 2. Define Shared State Interface Container
class ReviewState(TypedDict):
    """Data object storing review inputs, semantic labels, and tailored replies."""
    review: str
    sentiment: Optional[Literal["positive", "negative"]]
    diagnosis: Optional[dict]
    response: Optional[str]


# 3. Define Graph Node Processes
def find_sentiment_node(state: ReviewState) -> dict:
    """Invokes structured sentiment extractors."""
    load_dotenv()
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.0).with_structured_output(SentimentSchema)
    
    print("\n[Stage 1] Classifying feedback sentiment profile...")
    prompt = f"Analyze the sentiment orientation of this customer review:\n\n'{state['review']}'"
    output: SentimentSchema = model.invoke(prompt)
    
    print(f"  Detected Label: {output.sentiment.upper()}")
    return {"sentiment": output.sentiment}


def check_sentiment_router(state: ReviewState) -> Literal["positive_response", "run_diagnosis"]:
    """Conditional interception router steering execution control flow."""
    if state["sentiment"] == "positive":
        return "positive_response"
    else:
        return "run_diagnosis"


def positive_response_node(state: ReviewState) -> dict:
    """Authoring engine formulating appreciative gratitude templates."""
    load_dotenv()
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    print("[Stage 2: Positive Route] Generating customized gratitude sequence...")
    prompt = (
        f"Draft a concise, warm and highly professional thank-you response for this review:\n\n"
        f"'{state['review']}'\n\n"
        f"Politely invite the client to explore advanced ecosystem tiers."
    )
    reply_text = model.invoke(prompt).content
    return {"response": reply_text}


def run_diagnosis_node(state: ReviewState) -> dict:
    """Executes granular technical diagnosis parsing against problematic reviews."""
    load_dotenv()
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.0).with_structured_output(DiagnosisSchema)
    
    print("[Stage 2: Negative Route] Diagnosing core operational impediments...")
    prompt = (
        f"Diagnose the structural issues communicated in this negative review:\n\n"
        f"'{state['review']}'\n\n"
        f"Extract core issue_type, tone, and urgency parameter mappings."
    )
    output: DiagnosisSchema = model.invoke(prompt)
    
    parsed_payload = output.model_dump()
    print(f"  Diagnosis Snapshot: {parsed_payload}")
    return {"diagnosis": parsed_payload}


def negative_response_node(state: ReviewState) -> dict:
    """Synthesizes empathetic, helpful remediation templates mapping specific diagnostics."""
    load_dotenv()
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    
    diag = state["diagnosis"]
    print("[Stage 3: Support Resolution] Composing tailored remediation protocol...")
    
    prompt = (
        f"You are a Senior Customer Support Technical Architect.\n"
        f"The client left a negative review experiencing a '{diag['issue_type']}' domain issue.\n"
        f"Their tone registers as '{diag['tone']}', and triage urgency evaluates as '{diag['urgency']}'.\n"
        f"Review text:\n'{state['review']}'\n\n"
        f"Draft an exceptionally helpful, reassuring, and solution-oriented remediation response."
    )
    reply_text = model.invoke(prompt).content
    return {"response": reply_text}


# 4. Compile Pipeline Map
def compile_support_agent():
    """Binds functional nodes and dynamic semantic router paths."""
    graph = StateGraph(ReviewState)
    
    graph.add_node("find_sentiment", find_sentiment_node)
    graph.add_node("positive_response", positive_response_node)
    graph.add_node("run_diagnosis", run_diagnosis_node)
    graph.add_node("negative_response", negative_response_node)
    
    graph.add_edge(START, "find_sentiment")
    
    # Register dynamic routing edge
    graph.add_conditional_edges("find_sentiment", check_sentiment_router)
    
    graph.add_edge("positive_response", END)
    graph.add_edge("run_diagnosis", "negative_response")
    graph.add_edge("negative_response", END)
    
    return graph.compile()


if __name__ == "__main__":
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("[CAUTION] OPENAI_API_KEY missing from environment configuration.")
        
    workflow = compile_support_agent()
    
    test_reviews = [
        "Absolutely unparalleled architectural layout. Using TypedDict constraints significantly stabilized our multi-agent orchestration codebases without adding custom boilerplate overhead.",
        "The authentication microservice continually encounters socket thread timeouts during load testing phases. We had to roll back production deployments twice due to unhandled promise rejections."
    ]
    
    print("--- Initializing Agentic Support Orchestrator Engine ---")
    for idx, r_text in enumerate(test_reviews, 1):
        print(f"\n{'='*60}\nPROCESSING REVIEW #{idx}\n{'='*60}")
        initial_payload: ReviewState = {
            "review": r_text,
            "sentiment": None,
            "diagnosis": None,
            "response": None
        }
        
        try:
            output = workflow.invoke(initial_payload)
            print(f"\nFINAL SYNTHESIZED RESPONSE:\n{output['response']}\n")
        except Exception as e:
            print(f"Agent Execution encountered error: {e}")
