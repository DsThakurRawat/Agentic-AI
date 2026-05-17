import os
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# PATTERN 1: INDEPENDENT SUBGRAPHS (PRIVATE STATE)
# ==========================================

# 1. Subgraph State (Different Schema)
class TranslationState(TypedDict):
    input_text: str
    target_lang: str
    translated_text: str

# 2. Subgraph Logic
sub_llm = ChatOpenAI(model="gpt-4o-mini")

def translation_node(state: TranslationState):
    print(f"--- SUBGRAPH: TRANSLATING TO {state['target_lang']} ---")
    prompt = f"Translate the following text to {state['target_lang']}:\n{state['input_text']}"
    res = sub_llm.invoke(prompt)
    return {"translated_text": res.content}

# 3. Build Subgraph
sub_builder = StateGraph(TranslationState)
sub_builder.add_node("translator", translation_node)
sub_builder.add_edge(START, "translator")
sub_builder.add_edge("translator", END)
translation_subgraph = sub_builder.compile()

# 4. Parent State
class ParentState(TypedDict):
    english_query: str
    final_response: str

# 5. Parent Logic (The Bridge)
def orchestrator_node(state: ParentState):
    print("--- PARENT: STARTING ORCHESTRATION ---")
    # EXPLICIT MAPPING: Map Parent Keys -> Subgraph Keys
    # We call .invoke() manually
    sub_res = translation_subgraph.invoke({
        "input_text": state["english_query"],
        "target_lang": "Hindi"
    })
    
    # EXPLICIT MAPPING: Map Subgraph Output -> Parent State
    return {"final_response": sub_res["translated_text"]}

# 6. Build Parent (Pattern 1)
parent_builder_1 = StateGraph(ParentState)
parent_builder_1.add_node("orchestrator", orchestrator_node)
parent_builder_1.add_edge(START, "orchestrator")
parent_builder_1.add_edge("orchestrator", END)
independent_pattern_app = parent_builder_1.compile()


# ==========================================
# PATTERN 2: SHARED STATE SUBGRAPHS (DIRECT INTEGRATION)
# ==========================================

# 1. Shared State Schema
class SharedState(TypedDict):
    query: str
    response_en: str
    response_hi: str

# 2. Subgraph Logic (Uses Shared Keys)
def shared_translation_node(state: SharedState):
    print("--- SHARED SUBGRAPH: TRANSLATING ---")
    res = sub_llm.invoke(f"Translate to Hindi: {state['response_en']}")
    return {"response_hi": res.content}

# 3. Build Shared Subgraph
shared_sub_builder = StateGraph(SharedState)
shared_sub_builder.add_node("inner_translator", shared_translation_node)
shared_sub_builder.add_edge(START, "inner_translator")
shared_sub_builder.add_edge("inner_translator", END)
shared_subgraph = shared_sub_builder.compile()

# 4. Parent Logic
def generate_en_node(state: SharedState):
    print("--- PARENT: GENERATING ENGLISH ---")
    res = sub_llm.invoke(state["query"])
    return {"response_en": res.content}

# 5. Build Parent (Pattern 2: Direct Addition)
parent_builder_2 = StateGraph(SharedState)
parent_builder_2.add_node("generator", generate_en_node)

# DIRECT INTEGRATION: Add compiled graph as a node
# LangGraph automatically manages the state flow
parent_builder_2.add_node("translator_subgraph", shared_subgraph)

parent_builder_2.add_edge(START, "generator")
parent_builder_2.add_edge("generator", "translator_subgraph")
parent_builder_2.add_edge("translator_subgraph", END)
shared_pattern_app = parent_builder_2.compile()


if __name__ == "__main__":
    print("\n--- RUNNING INDEPENDENT PATTERN ---")
    res1 = independent_pattern_app.invoke({"english_query": "Hello, how are you?"})
    print(f"Result: {res1['final_response']}")
    
    print("\n--- RUNNING SHARED PATTERN ---")
    res2 = shared_pattern_app.invoke({"query": "What is the capital of France?"})
    print(f"EN: {res2['response_en']}")
    print(f"HI: {res2['response_hi']}")
