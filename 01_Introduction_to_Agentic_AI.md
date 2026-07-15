# Session 01 — Introduction to Agentic AI

---

## 1. What is Generative AI? (Quick Recap)

Generative AI (GenAI) refers to AI models that generate content — text, images, code, audio — based on a given prompt.

**Examples:** ChatGPT, Claude, Gemini, DALL·E

**How it works:**
- User gives a prompt → Model generates a response → Done.
- It is **reactive** — it only does something when asked.
- It has **no memory** beyond the conversation window.
- It **cannot take actions** in the real world on its own.

**Limitation:** GenAI is great for answering questions, but it cannot autonomously complete multi-step tasks.

---

## 2. What is Agentic AI?

Agentic AI refers to AI systems that can **plan, reason, make decisions, and take actions autonomously** to achieve a goal — without needing a human to guide every step.

> "If GenAI is a brilliant advisor who gives you answers, Agentic AI is a capable employee who gets the job done."

**Core idea:** Instead of just generating text, an Agentic AI can:
- Break a complex goal into smaller steps (Planning)
- Remember previous steps and context (Memory)
- Use external tools — APIs, databases, code runners (Tool Use)
- Decide what to do next based on results (Reasoning Loop)

---

## 3. Key Concepts in Agentic AI

### 3.1 Reasoning
The AI can think through a problem step-by-step before acting.

**Example pattern — ReAct (Reason + Act):**
```
Thought: I need to find the current weather in London.
Action: Call weather API with city=London
Observation: Temperature is 15°C, cloudy.
Thought: Now I have the data. I can answer the user.
Answer: The current weather in London is 15°C and cloudy.
```

### 3.2 Memory
Agents need memory to maintain context across steps.

| Memory Type | Description | Example |
|---|---|---|
| Short-term | Within a single session | Conversation history |
| Long-term | Across sessions | Stored in a vector database |
| Entity memory | Remembers specific people/things | "User prefers Python examples" |

### 3.3 Tool Use
Agents can call external tools to fetch real-world data or perform actions.

**Common tools:**
- Web search (Google, DuckDuckGo)
- Calculator
- Code executor
- Database queries
- REST API calls
- File read/write

### 3.4 The Agent Loop
```
Goal → Plan → Act (use tool) → Observe result → Reason → Plan next step → ... → Final Answer
```
This loop continues until the agent decides it has achieved the goal.

---

## 4. Agentic AI vs. Generative AI — Side by Side

| Feature | Generative AI | Agentic AI |
|---|---|---|
| **Input** | Single prompt | A goal or task |
| **Output** | Single response | Series of actions + final result |
| **Memory** | Limited (context window) | Short-term + long-term memory |
| **Tool use** | No | Yes — APIs, databases, code, etc. |
| **Decision making** | No | Yes — decides next steps |
| **Autonomy** | Reactive | Proactive & autonomous |
| **Multi-step tasks** | Poor | Designed for this |
| **Examples** | ChatGPT, Claude chat | LangChain Agents, AutoGen, CrewAI |

---

## 5. Real-World Use Cases

| Use Case | How Agentic AI Helps |
|---|---|
| **Customer Support Bot** | Looks up order status, processes refunds, escalates tickets — all autonomously |
| **Research Assistant** | Searches the web, reads documents, summarizes findings |
| **Code Assistant** | Writes code, runs tests, debugs errors, iterates until working |
| **Data Analyst Agent** | Queries databases, generates charts, writes reports |
| **HR Recruiting Agent** | Screens resumes, schedules interviews, sends emails |
| **Finance Agent** | Fetches stock data, runs calculations, generates investment summaries |

---

## 6. Key Frameworks for Building Agentic AI

| Framework | Description |
|---|---|
| **LangChain** | Most popular; modular; supports agents, chains, memory, tools |
| **LangGraph** | Graph-based multi-agent workflows (built on LangChain) |
| **CrewAI** | Multi-agent collaboration — assign roles like a team |
| **AutoGen** | Microsoft's multi-agent conversation framework |
| **Claude Agent SDK** | Anthropic's native SDK for building Claude-powered agents |

---

## 7. Summary

- **GenAI** = generates responses to prompts (reactive, one-shot)
- **Agentic AI** = plans, reasons, uses tools, and acts autonomously (proactive, multi-step)
- Three pillars of Agentic AI: **Reasoning + Memory + Tool Use**
- The **Agent Loop** is the engine: Think → Act → Observe → Repeat
- **LangChain** is the framework we'll use to build these agents

---

> **Next Session →** Session 02: LangChain — Building Agents with Claude
