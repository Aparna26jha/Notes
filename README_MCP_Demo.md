# Real MCP Demo: Order Support

This package contains:

- `support_mcp_server.py` → real MCP server exposing tools
- `mcp_langgraph_client.py` → LangGraph + Anthropic client that connects to the MCP server
- `requirements.txt`
- `.env.example`

## Install

```bash
pip install -r requirements.txt
```

## Configure

Copy `.env.example` to `.env` and add your real key.

## Run

```bash
python mcp_langgraph_client.py
```

The client launches the local MCP server through FastMCP client transport and then runs test queries.
