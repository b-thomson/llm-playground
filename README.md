# llm-playground

A monorepo of small, self-contained AI experiments.

## Projects

### [memory-chat](projects/memory-chat/)
A minimal Streamlit chat app with provider/model selection and configurable conversation memory. Supports OpenAI, Anthropic, and Google out of the box.

### [memory-chat-persistent](projects/memory-chat-persistent/)
Extends memory-chat with SQLite-backed session persistence. Chat history survives app restarts. Multiple named sessions supported.

### [memory-chat-tools](projects/memory-chat-tools/)
Adds Anthropic tool use to the persistent app. The model can call a web search tool (Tavily) mid-conversation, loop until it has enough information, and incorporate live results into its response.

### [context-inspector](projects/context-inspector/)
Extends memory-chat-tools with a live inspector sidebar. Chat in the main area with an inspector sidebar. Every turn exposes its raw message JSON, direction badges, and a running prior-context count so context window accumulation is visible.

## Setup

1. Clone the repo
2. Copy `.env.example` to `.env` and add your API keys
3. `cd projects/<name>` and run `uv run streamlit run app.py`

## Structure

```
llm-playground/
├── .env          # Shared API keys (not committed)
└── projects/
    ├── memory-chat/
    ├── memory-chat-persistent/
    ├── memory-chat-tools/
    └── context-inspector/
```