# llm-playground

A monorepo of small, self-contained AI experiments.

## Projects

### [memory-chat](projects/memory-chat/)
A minimal Streamlit chat app with provider/model selection and configurable conversation memory. Supports OpenAI, Anthropic, and Google out of the box.

### [memory-chat-persistent](projects/memory-chat-persistent/)
Extends memory-chat with SQLite-backed session persistence. Chat history survives app restarts. Multiple named sessions supported.

## Setup

1. Clone the repo
2. Copy `.env.example` to `.env` and add your API keys
3. `cd` into a project and run it (see the project's own README)

## Structure

```
llm-playground/
├── .env          # Shared API keys (not committed)
└── projects/
    └── memory-chat/
```