"""
Production Multi-Dimensional Essay Evaluation Workflow
Translates `5_UPSC_essay_workflow.ipynb` demonstrating custom list reducers and Pydantic validation.
"""

import os
import operator
from typing import TypedDict, Annotated, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END


# 1. Define Structured Output Validation Schema
class EvaluationSchema(BaseModel):
    """Pydantic definition ensuring model validation output consistency."""
    feedback: str = Field(description="Detailed actionable feedback critique")
    score: int = Field(description="Quantitative score out of 10", ge=0, le=10)


# 2. Define Shared State Interface
class UPSCState(TypedDict):
    """
    State container leveraging custom reducers.
    'operator.add' appends parallel array returns together without key overwrites.
    """
    essay: str
    language_feedback: Optional[str]
    analysis_feedback: Optional[str]
    clarity_feedback: Optional[str]
    overall_feedback: Optional[str]
    individual_scores: Annotated[list[int], operator.add]
    avg_score: Optional[float]


# 3. Define Parallel Evaluation Nodes
def evaluate_language(state: UPSCState) -> dict:
    """Evaluates written grammar attributes concurrently."""
    load_dotenv()
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.0).with_structured_output(EvaluationSchema)
    
    print("[Agent 1] Evaluating language precision and syntactic flow...")
    prompt = f"Evaluate the language quality of this essay. Return structured feedback and a score out of 10:\n\n{state['essay']}"
    output: EvaluationSchema = model.invoke(prompt)
    
    return {"language_feedback": output.feedback, "individual_scores": [output.score]}


def evaluate_analysis(state: UPSCState) -> dict:
    """Evaluates analytical depth attributes concurrently."""
    load_dotenv()
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.0).with_structured_output(EvaluationSchema)
    
    print("[Agent 2] Evaluating logical framing and analytical depth...")
    prompt = f"Evaluate the depth of analysis of this essay. Return structured feedback and a score out of 10:\n\n{state['essay']}"
    output: EvaluationSchema = model.invoke(prompt)
    
    return {"analysis_feedback": output.feedback, "individual_scores": [output.score]}


def evaluate_thought(state: UPSCState) -> dict:
    """Evaluates structural clarity attributes concurrently."""
    load_dotenv()
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.0).with_structured_output(EvaluationSchema)
    
    print("[Agent 3] Evaluating clarity of thought and argument cohesion...")
    prompt = f"Evaluate the clarity of thought of this essay. Return structured feedback and a score out of 10:\n\n{state['essay']}"
    output: EvaluationSchema = model.invoke(prompt)
    
    return {"clarity_feedback": output.feedback, "individual_scores": [output.score]}


def final_evaluation(state: UPSCState) -> dict:
    """Aggregates list states and consensus feedbacks downstream."""
    load_dotenv()
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    
    print("\n[Consensus Agent] Synthesizing final aggregate evaluation envelope...")
    
    prompt = (
        f"Synthesize an executive summary feedback based on these isolated critiques:\n"
        f"1. Language: {state['language_feedback']}\n"
        f"2. Analysis Depth: {state['analysis_feedback']}\n"
        f"3. Argument Clarity: {state['clarity_feedback']}"
    )
    summary_text = model.invoke(prompt).content
    
    scores = state["individual_scores"]
    avg = sum(scores) / len(scores) if scores else 0.0
    
    return {"overall_feedback": summary_text, "avg_score": round(avg, 2)}


# 4. Compile Parallel Processing Architecture
def compile_evaluation_engine():
    """Builds concurrent evaluation maps converging onto consensus outputs."""
    graph = StateGraph(UPSCState)
    
    graph.add_node("evaluate_language", evaluate_language)
    graph.add_node("evaluate_analysis", evaluate_analysis)
    graph.add_node("evaluate_thought", evaluate_thought)
    graph.add_node("final_evaluation", final_evaluation)
    
    graph.add_edge(START, "evaluate_language")
    graph.add_edge(START, "evaluate_analysis")
    graph.add_edge(START, "evaluate_thought")
    
    graph.add_edge("evaluate_language", "final_evaluation")
    graph.add_edge("evaluate_analysis", "final_evaluation")
    graph.add_edge("evaluate_thought", "final_evaluation")
    
    graph.add_edge("final_evaluation", END)
    
    return graph.compile()


if __name__ == "__main__":
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("[CAUTION] OPENAI_API_KEY missing from environment configuration.")
        
    workflow = compile_evaluation_engine()
    
    sample_essay = (
        "Artificial Intelligence represents a major technological inflection point for modern software architecture. "
        "By allowing deterministic pipelines to interface with probabilistic semantic reasoning layers, developers "
        "can build resilient autonomous applications capable of self-correction, parallel map reductions, and complex "
        "multi-agent orchestration topologies. However, without clear bounds and static compilation verification checks, "
        "these agentic workflows risk context overflow and excessive token latency overhead."
    )
    
    initial_payload: UPSCState = {
        "essay": sample_essay,
        "language_feedback": None,
        "analysis_feedback": None,
        "clarity_feedback": None,
        "overall_feedback": None,
        "individual_scores": [],
        "avg_score": None
    }
    
    try:
        final_state = workflow.invoke(initial_payload)
        print("\n" + "="*55)
        print("FINAL EVALUATED CRITIQUE REPORT")
        print("="*55)
        print(f"Aggregated Sub-Scores array: {final_state['individual_scores']}")
        print(f"Calculated Mean Score: {final_state['avg_score']} / 10.0\n")
        print("EXECUTIVE FEEDBACK SUMMARY:")
        print(final_state["overall_feedback"])
    except Exception as e:
        print(f"Pipeline Execution triggered error: {e}")
