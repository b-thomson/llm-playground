# PRD — memory-chat

## What is it?
A minimal web-based LLM chat app with provider/model selection and configurable conversation memory.

## Why
To ship something, break inertia, and start a public GitHub portfolio of agentic AI experiments.

## Who
Primarily the author. Secondarily: other amateur agentic AI devs who find the repo.

## Features
- Streamlit UI
- Chat input with two dropdowns: provider and model
  - Supported providers: OpenAI, Anthropic, Google
  - Each provider has 3 models: default (best cost/performance), premium, lite
  - Switching provider auto-selects that provider's default model
- Memory dropdown: 1–10 user/assistant pairs kept in context
- Rolling chat history displayed on screen for the session
- All state is in-session only — nothing persists on restart

## Default models
- OpenAI: gpt-4o-mini (default), gpt-4o (premium), gpt-3.5-turbo (lite)
- Anthropic: claude-sonnet-4-6 (default), claude-opus-4-7 (premium), claude-haiku-4-5 (lite)
- Google: gemini-2.0-flash (default), gemini-2.5-pro (premium), gemini-2.0-flash-lite (lite)

## Out of scope (v1)
- API key entry in UI
- Session persistence / memory across restarts
- Context window inspection tool
- Auth, multi-user, deployment

## Success criteria
- App loads with OpenAI + default model selected
- Can switch provider/model, send a message, get a response
- Memory dropdown correctly limits context window to N pairs
- Chat history visible on screen for the session

## v2 ideas
- API key management in UI
- Session save/restore
- RAG + vector DB
- Context window inspector