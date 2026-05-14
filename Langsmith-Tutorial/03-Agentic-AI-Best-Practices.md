# What Agentic AI & GenAI Engineers Must Do with LangSmith

As of May 2026, building production-grade GenAI is highly complex. Agentic AI involves autonomous systems that plan, use tools, and correct their own errors. Here are the **mandatory best practices and workflows** that every Agentic AI engineer should implement using LangSmith.

## 1. Instrument Agent Native Architectures
Agentic systems (like those built with **LangGraph**) require more than standard request/response tracing.
- **Track Multi-Agent Handoffs:** Ensure your tracing captures when an agent delegates a task to a sub-agent (e.g., a "Supervisor" agent passing work to a "Researcher" agent).
- **Monitor Tool Fidelity:** Track not just that a tool was called, but *how often* an agent hallucinates tool arguments or gets stuck in a loop calling the same tool repeatedly.

## 2. Turn Production Traces into Evaluation Datasets
You cannot improve what you cannot measure. 
- **Identify Edge Cases:** When you spot a failed trace in production (e.g., the agent gave a dangerous or incorrect answer), add that trace directly to a **LangSmith Dataset** with a single click.
- **Create Golden Datasets:** Build curated datasets of inputs and expected outputs. Before deploying a new prompt or changing from `gpt-4o` to a smaller, faster model, run your application against this dataset in LangSmith to guarantee no regressions.

## 3. Implement Automated Evaluations (Evals)
Manual testing is dead. Use LangSmith's Evaluation framework.
- **LLM-as-a-Judge:** Configure LangSmith to automatically run a secondary, highly capable LLM (like GPT-4o or Claude 3.5 Sonnet) over your agent's responses to score them on metrics like:
  - *Contextual Relevance* (Did it answer the question?)
  - *Faithfulness* (Did it hallucinate facts?)
  - *Toxicity / Tone*
- **Continuous Integration (CI/CD):** Integrate LangSmith evals into your GitHub Actions. If a pull request degrades the agent's accuracy score by 10%, block the merge.

## 4. Leverage the Prompt Hub for Collaboration
Hardcoding prompts in Python files is an anti-pattern.
- Use LangSmith's **Prompt Hub** to version control your system prompts.
- Allow domain experts (who may not be engineers) to tweak the prompt in the LangSmith UI, run it against the evaluation dataset, and publish a new version. Your code then simply pulls the latest commit of the prompt from the Hub via API.

## 5. Implement User Feedback Loops
- Add simple thumbs-up / thumbs-down buttons to your chatbot UI.
- Bind these actions to LangSmith via the SDK. LangSmith will automatically correlate the user's feedback with the exact trace that generated the response.
- Use the **Insights Agent** to automatically cluster low-score traces to identify systemic issues (e.g., "The agent always fails when asked about billing policies").
