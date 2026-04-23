# TECH_SPEC — memory-chat-tools

## Stack
- Python 3.12
- Streamlit (UI)
- Anthropic SDK (LLM + tool use)
- Tavily Python SDK (web search)
- SQLite stdlib (session persistence)
- python-dotenv (env vars from root .env)

## Tool Definition
```python
TOOLS = [{
    "name": "web_search",
    "description": "Search the web for current information. Use when asked about recent events, current data, or anything you might not know.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query"}
        },
        "required": ["query"]
    }
}]
```

## Agentic Loop
```
user message
    → messages.create(tools=TOOLS)
    → if stop_reason == "tool_use":
        → execute_tool(name, input) → result string
        → append assistant content (tool_use blocks) to messages
        → append user content (tool_result blocks) to messages
        → loop back to messages.create
    → if stop_reason == "end_turn":
        → extract text block → return to UI
```

## Message Format
All messages stored in SQLite with content serialised as JSON. Content may be:
- `str` — simple user/assistant text (legacy compat)
- `list[dict]` — Anthropic content blocks (tool_use, tool_result, text)

On load: `json.loads(content)` → pass directly to Anthropic API.

## DB Schema
Same as memory-chat-persistent:
```sql
CREATE TABLE sessions (id, name, created_at);
CREATE TABLE messages (id, session_id, role, content TEXT, created_at);
```
`content` stores JSON string always.

## UI
- Session selector row (same as memory-chat-persistent)
- Model selector (Anthropic models only: opus/sonnet/haiku)
- Chat area:
  - User messages: plain text
  - Tool calls: `st.info("Searching: {query}")` inline
  - Final assistant text: markdown
- chat_input disabled when no session active

## File Layout
```
memory-chat-tools/
├── app.py
├── PRD.md
├── TECH_SPEC.md
├── TODO.md
├── README.md
├── pyproject.toml
├── uv.lock
└── tests/
    └── test_tool.py
```

## Env Vars Required
- `ANTHROPIC_API_KEY`
- `TAVILY_API_KEY`