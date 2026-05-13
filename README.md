# 🕸️ Agentic AI Mastery Track using LangGraph

*A dedicated repository implementation following structural programming tutorials, cyclical State Machine patterns, multi-agent frameworks, and external tool integration strategies compatible with **LangGraph Studio**.*

---

## 🏛️ Repository Organization

```text
Agentic-AI/
├── starter_kit/           # Modular starter template pre-configured for standalone execution & Studio
│   ├── state.py           # Custom TypedDict AgentState schema with reducer annotations
│   ├── tools.py           # Dynamic tool definitions bound directly to inference models
│   ├── nodes.py           # Execution processing blocks mapping deterministic step routines
│   ├── graph.py           # Core graph topology construction, checkpointer wiring, and routing
│   └── langgraph.json     # Configuration manifest for immediate LangGraph Studio integration
└── .env.example           # Infrastructure keys template required for model calls and tracing
```

---

## 🚀 Execution Guide

### Running Starter Workflows Locally
Verify state machine execution via local thread checkpointers directly:

```bash
# Ensure your virtual environment containing langgraph is activated, e.g.:
# source /home/divyansh-rawat/Agentic-AI/venv/bin/activate

cd starter_kit
python3 graph.py
```

### Initializing LangGraph Studio
1. Launch **LangGraph Studio** desktop client.
2. Select the `starter_kit/` folder or root workspace project directory.
3. The integrated client dynamically parses routing rules mapped inside `langgraph.json` to stream execution steps visually.
# Agentic-AI
