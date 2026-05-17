import os
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the State
class AgentState(TypedDict):
    topic: str
    research: str
    draft: str
    approved: bool

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# Node 1: Research
def research_node(state: AgentState):
    print(f"--- RESEARCHING TOPIC: {state['topic']} ---")
    response = llm.invoke(f"Provide a 2-sentence summary about {state['topic']} for a social media post.")
    return {"research": response.content}

# Node 2: Draft Post (HITL Point)
def post_node(state: AgentState):
    print("--- GENERATING DRAFT POST ---")
    draft_response = llm.invoke(f"Based on this research: {state['research']}, write a catchy X (Twitter) post with hashtags.")
    
    # TRIGGER INTERRUPT: This pauses the graph and waits for human input
    # The payload passed to interrupt() is what the human/UI will see
    human_review = interrupt({
        "question": "Please review the generated draft post.",
        "draft": draft_response.content,
        "instructions": "Type 'y' to approve, or type your edits to modify the post."
    })
    
    # If the human provided edits instead of just 'y', we update the draft
    if human_review.lower() != 'y':
        print("--- HUMAN EDITED THE POST ---")
        return {"draft": human_review, "approved": True}
    
    print("--- HUMAN APPROVED THE POST ---")
    return {"draft": draft_response.content, "approved": True}

# Build the Graph
builder = StateGraph(AgentState)

builder.add_node("research", research_node)
builder.add_node("post", post_node)

builder.add_edge(START, "research")
builder.add_edge("research", "post")
builder.add_edge("post", END)

# Compile with Memory (required for HITL)
memory = MemorySaver()
app = builder.compile(checkpointer=memory)

# --- EXECUTION FLOW ---
if __name__ == "__main__":
    thread_config = {"configurable": {"thread_id": "sm_manager_01"}}
    
    # 1. Initial invocation (Frontend: Enter Topic -> Submit)
    topic = "The impact of Agentic AI on Software Engineering"
    print(f"\n[FRONTEND] User submitted topic: {topic}")
    
    # Start the graph
    result = app.invoke({"topic": topic}, config=thread_config)
    
    # 2. Check for Interrupt
    if "__interrupt__" in result:
        interrupt_data = result["__interrupt__"][0].value
        print(f"\n[HITL INTERRUPT] {interrupt_data['question']}")
        print(f"Draft Post: \n{interrupt_data['draft']}")
        
        # Simulate Human Input
        human_input = input(f"\n{interrupt_data['instructions']}\n> ")
        
        # 3. Resume the Graph
        print("\n--- RESUMING GRAPH ---")
        final_state = app.invoke(Command(resume=human_input), config=thread_config)
        
        print("\n[FINAL POST]")
        print(final_state["draft"])
        print("\n--- WORKFLOW COMPLETE ---")
