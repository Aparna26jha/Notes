# Session 02 — LangChain: Building Agents with Claude

---

## 1. What is LangChain?

LangChain is an **open-source framework** for building applications powered by Large Language Models (LLMs).

It provides ready-made building blocks for:
- Connecting to LLMs (like Claude, GPT, Gemini)
- Creating prompt templates
- Chaining multiple steps together
- Adding memory to conversations
- Giving AI access to tools
- Building full autonomous agents

> "LangChain turns an LLM from a text generator into a thinking, acting system."

---

## 2. Why LangChain with Claude?

| Reason | Detail |
|---|---|
| **Claude is powerful** | Anthropic's Claude excels at reasoning, following instructions, and tool use |
| **Native integration** | `langchain-anthropic` provides a first-class Claude integration |
| **Safety-first** | Claude is designed with safety and reliability in mind — ideal for agents |
| **Large context window** | Claude supports up to 200K tokens — great for long documents and memory |

---

## 3. Setup & Installation

### 3.1 Install packages
```bash
pip install langchain langchain-core langchain-anthropic anthropic python-dotenv
```

### 3.2 Set your API key
Create a `.env` file in your project root:
```
ANTHROPIC_API_KEY=your-api-key-here
```

### 3.3 Load the key in Python
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 4. Basic LLM Integration — Calling Claude

This is the simplest possible use of LangChain with Claude.

```python
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()

# Initialize the Claude model
llm = ChatAnthropic(model="claude-sonnet-4-6")

# Send a simple message
response = llm.invoke("What is Agentic AI?")
print(response.content)
```

**What's happening:**
- `ChatAnthropic` wraps the Claude API in LangChain's standard interface
- `.invoke()` sends a message and returns a response
- The same interface works for GPT, Gemini, etc. — just swap the class

---

## 5. Prompt Templates

Instead of hardcoding prompts, LangChain uses **PromptTemplates** — reusable prompt structures with variables.

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()

llm = ChatAnthropic(model="claude-sonnet-4-6")

# Define a reusable prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in {domain}. Answer clearly and concisely."),
    ("human", "{question}")
])

# Fill in the variables and call Claude
chain = prompt | llm

response = chain.invoke({
    "domain": "Agentic AI",
    "question": "What is the difference between an agent and a chain?"
})

print(response.content)
```

**Key concepts:**
- `{variable}` — placeholders filled at runtime
- `system` message — sets Claude's role/persona
- `human` message — the actual user question
- `|` operator — connects prompt → LLM (this is a **chain**)

---

## 6. Prompt Chaining

Prompt chaining means the **output of one step becomes the input of the next**.

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()

llm = ChatAnthropic(model="claude-sonnet-4-6")
parser = StrOutputParser()

# Step 1: Generate a topic summary
summary_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a technical educator."),
    ("human", "Summarize the topic '{topic}' in 3 bullet points.")
])

# Step 2: Turn the summary into quiz questions
quiz_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a quiz generator."),
    ("human", "Based on this summary:\n{summary}\n\nCreate 2 multiple-choice questions.")
])

# Build the chain: topic → summary → quiz
summary_chain = summary_prompt | llm | parser
quiz_chain = quiz_prompt | llm | parser

# Run Step 1
summary = summary_chain.invoke({"topic": "Agentic AI"})
print("=== Summary ===")
print(summary)

# Run Step 2 using Step 1's output
quiz = quiz_chain.invoke({"summary": summary})
print("\n=== Quiz Questions ===")
print(quiz)
```

**What's happening:**
- Step 1: Claude summarizes the topic
- Step 2: Claude takes that summary and creates quiz questions
- Each step's output feeds into the next — this is **chaining**

---

## 7. Adding Memory to Conversations

Without memory, every message to Claude starts fresh. With memory, the agent remembers past conversation.

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatAnthropic(model="claude-sonnet-4-6")

# Maintain conversation history manually
history = []

def chat(user_input):
    history.append(HumanMessage(content=user_input))
    response = llm.invoke(history)
    history.append(AIMessage(content=response.content))
    return response.content

# Simulate a multi-turn conversation
print(chat("My name is Alex. I'm learning about LangChain."))
print(chat("What did I just tell you my name was?"))
print(chat("What topic am I learning about?"))
```

**Key insight:** Memory is just a list of messages passed to the LLM each time. LangChain provides higher-level memory classes (`ConversationBufferMemory`, `ConversationSummaryMemory`) that manage this automatically.

---

## 8. Tool Use — Giving Claude Capabilities

Tools let Claude take real actions: search the web, run code, query databases, etc.

```python
from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

llm = ChatAnthropic(model="claude-sonnet-4-6")

# Define tools available to the agent
tools = [DuckDuckGoSearchRun()]

# Agent prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use tools when needed."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Create the agent
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Run the agent with a real-world question
result = agent_executor.invoke({
    "input": "What is the latest news about Agentic AI in 2025?"
})

print(result["output"])
```

**What's happening:**
- Claude receives the question
- It decides it needs to search the web
- It calls `DuckDuckGoSearchRun` with a search query
- It reads the results and formulates a final answer
- `verbose=True` shows the agent's thinking process step by step

---

## 9. Creating a Full Agent

A complete agent with system role, tools, memory, and reasoning:

```python
from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatAnthropic(model="claude-sonnet-4-6")

# Tools
tools = [
    DuckDuckGoSearchRun(),
    WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
]

# Prompt with memory placeholder
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an intelligent research assistant.
    You have access to web search and Wikipedia.
    Always think step by step before answering.
    Be concise and cite your sources."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Build agent
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Conversation with memory
chat_history = []

def run_agent(user_input):
    result = agent_executor.invoke({
        "input": user_input,
        "chat_history": chat_history
    })
    chat_history.append(HumanMessage(content=user_input))
    chat_history.append(AIMessage(content=result["output"]))
    return result["output"]

# Test the agent
print(run_agent("What is LangChain and who created it?"))
print(run_agent("How does it compare to AutoGen?"))
```

---

## 10. LangChain Architecture — Big Picture

```
User Input
    ↓
Prompt Template  ← fills in variables
    ↓
LLM (Claude)     ← reasons about the task
    ↓
Tool Call?  ──Yes──→  Tool Execution  ──→  Back to LLM
    ↓ No
Output Parser    ← formats the response
    ↓
Final Answer → User
```

**Core components:**

| Component | Role |
|---|---|
| `ChatAnthropic` | Connects to Claude API |
| `ChatPromptTemplate` | Structures the prompt with variables |
| `StrOutputParser` | Parses LLM output into plain text |
| `Tools` | External capabilities (search, calculator, etc.) |
| `AgentExecutor` | Runs the agent loop (Think → Act → Observe) |
| `Memory` | Stores conversation history |
| `Chain ( | )` | Connects components in sequence |

---

## 11. Summary

| Concept | What It Does |
|---|---|
| **Basic LLM call** | Send a message to Claude, get a response |
| **Prompt Template** | Reusable prompts with dynamic variables |
| **Prompt Chaining** | Output of one step becomes input of next |
| **Memory** | Persist conversation history across turns |
| **Tool Use** | Give Claude real-world capabilities |
| **Agent** | Claude autonomously decides which tools to use and when |

---

## 12. Discussion Order Recap

| Order | Session | Topic |
|---|---|---|
| **First** | Session 01 | Introduction to Agentic AI — Concepts, GenAI vs Agentic AI, Use Cases |
| **Second** | Session 02 | LangChain — Basic LLM integration, Prompt Chaining, Agent Creation |

---

> Start with **concepts** before **code** — participants need the "why" before the "how."
