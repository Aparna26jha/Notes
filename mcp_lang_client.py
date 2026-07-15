# ──────────────────────────────────────────────────────────────
# 1. ENV SETUP
# ──────────────────────────────────────────────────────────────
import os
import asyncio
import operator
from typing import TypedDict, Annotated, Literal, Any

from dotenv import load_dotenv

load_dotenv(override=True)

llmgw_api_key = os.getenv("LLMGW_API_KEY")
llmgw_base_url = os.getenv("LLMGW_BASE_URL", "https://llmgw-wp.tekstac.com")

if not llmgw_api_key:
    raise ValueError("LLMGW_API_KEY not found. Add it to your .env file.")

# Anthropic-compatible env vars
os.environ["ANTHROPIC_API_KEY"] = llmgw_api_key
os.environ["ANTHROPIC_BASE_URL"] = llmgw_base_url

print("=" * 60)
print("ENVIRONMENT STATUS")
print("=" * 60)
print(f"LLMGW_API_KEY  : {'✅ set' if llmgw_api_key else '❌ missing'}")
print(f"LLMGW_BASE_URL : {llmgw_base_url}")
print("=" * 60)

# ──────────────────────────────────────────────────────────────
# 2. IMPORTS
# ──────────────────────────────────────────────────────────────
from fastmcp import Client
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, ToolMessage, BaseMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

# Path to MCP server
MCP_SERVER_SOURCE = "support_mcp_server.py"

# ──────────────────────────────────────────────────────────────
# 3. MODEL SETUP
# ──────────────────────────────────────────────────────────────
chat_model = ChatAnthropic(
    model="global.anthropic.claude-sonnet-4-6",
    temperature=0.3,
    anthropic_api_key=llmgw_api_key,
    base_url=llmgw_base_url,
)

# ──────────────────────────────────────────────────────────────
# 4. MCP HELPERS
# ──────────────────────────────────────────────────────────────
def convert_mcp_tool_to_anthropic_schema(tool_obj: Any) -> dict:
    """
    Convert FastMCP tool metadata into Anthropic-compatible tool schema.
    """
    input_schema = getattr(tool_obj, "inputSchema", None) or getattr(tool_obj, "input_schema", None)

    return {
        "name": tool_obj.name,
        "description": getattr(tool_obj, "description", "") or "",
        "input_schema": input_schema or {
            "type": "object",
            "properties": {},
            "required": []
        }
    }


async def fetch_mcp_tool_schemas() -> list[dict]:
    """
    Connect to MCP server and discover tools.
    """
    client = Client(MCP_SERVER_SOURCE)

    async with client:
        tools = await client.list_tools()

    schemas = [convert_mcp_tool_to_anthropic_schema(t) for t in tools]
    return schemas


def normalize_mcp_result(result: Any) -> str:
    """
    Normalize MCP tool call result into text.
    FastMCP may return text directly or a structured content object.
    """
    if result is None:
        return ""

    # If plain string
    if isinstance(result, str):
        return result

    # If object has content
    if hasattr(result, "content"):
        content = result.content

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            text_parts = []
            for part in content:
                if isinstance(part, str):
                    text_parts.append(part)
                else:
                    text = getattr(part, "text", None)
                    if text:
                        text_parts.append(text)
            if text_parts:
                return "\n".join(text_parts)

    return str(result)


async def call_mcp_tool(tool_name: str, args: dict) -> str:
    """
    Connect to MCP server and execute one tool call.
    """
    client = Client(MCP_SERVER_SOURCE)

    async with client:
        result = await client.call_tool(tool_name, args)

    return normalize_mcp_result(result)


# ──────────────────────────────────────────────────────────────
# 5. AGENT STATE
# ──────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]


# ──────────────────────────────────────────────────────────────
# 6. BUILD TOOL-AWARE MODEL
# ──────────────────────────────────────────────────────────────
async def get_llm_with_mcp_tools():
    tool_schemas = await fetch_mcp_tool_schemas()
    return chat_model.bind_tools(tool_schemas)


# ──────────────────────────────────────────────────────────────
# 7. GRAPH NODES
# ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = SystemMessage(
    content=(
        "You are a customer support assistant. "
        "Use available MCP tools when needed. "
        "If the user asks about an order and does not provide an order ID, ask for it clearly. "
        "If the user asks about refund eligibility, use the refund tool when the number of days is available."
    )
)


async def support_agent_node(state: AgentState):
    """
    LLM decides whether to answer directly or call one/more MCP tools.
    """
    llm_with_tools = await get_llm_with_mcp_tools()

    messages = state["messages"]

    # prepend system prompt once per invocation
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SYSTEM_PROMPT] + messages

    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}


async def tool_execution_node(state: AgentState):
    """
    Execute MCP tool calls requested by the LLM.
    """
    last_message = state["messages"][-1]
    results = []

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        print(f"[MCP CLIENT] Calling tool: {tool_name} | args: {tool_args}")

        tool_output = await call_mcp_tool(tool_name, tool_args)

        results.append(
            ToolMessage(
                content=tool_output,
                tool_call_id=tool_call["id"],
            )
        )

    return {"messages": results}


# ──────────────────────────────────────────────────────────────
# 8. ROUTING LOGIC
# ──────────────────────────────────────────────────────────────
def route_next_step(state: AgentState) -> Literal["tools", "__end__"]:
    """
    If the last AI message contains tool calls, go to tools.
    Otherwise, finish.
    """
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return END


# ──────────────────────────────────────────────────────────────
# 9. BUILD GRAPH
# ──────────────────────────────────────────────────────────────
workflow = StateGraph(AgentState)

workflow.add_node("agent", support_agent_node)
workflow.add_node("tools", tool_execution_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", route_next_step)
workflow.add_edge("tools", "agent")

app = workflow.compile()


# ──────────────────────────────────────────────────────────────
# 10. RUN TEST QUERIES
# ──────────────────────────────────────────────────────────────
queries = [
    "Hi, where is my order ORD123?",
    "Is ORD321 delivered yet?",
    "I bought something 45 days ago, can I get refund?",
    "Check ORD999 and also tell refund for 10 days purchase",
    "What about order ORD888?",
    "Where is my order?"
]

async def main():
    print("\n--- REAL MCP + LangGraph Support Bot Running ---")

    # connection smoke test
    try:
        test = await chat_model.ainvoke("Capital of France?")
        print(f"\n✅ LLM connection OK: {test.content}")
    except Exception as e:
        print(f"❌ LLM connection Error: {e}")
        return

    # MCP discovery smoke test
    try:
        tool_schemas = await fetch_mcp_tool_schemas()
        print("\n✅ MCP tools discovered:")
        for tool in tool_schemas:
            print(f" - {tool['name']}")
    except Exception as e:
        print(f"❌ MCP discovery error: {e}")
        return

    for query in queries:
        print(f"\nUser: {query}")

        result = await app.ainvoke({
            "messages": [HumanMessage(content=query)]
        })

        final_message = result["messages"][-1].content
        print(f"Bot: {final_message}")


if __name__ == "__main__":
    asyncio.run(main())
