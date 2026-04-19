# PRD — memory-chat-persistent

## What is it?
Extends memory-chat with SQLite-backed session persistence. Chat history survives app restarts.

## Builds on
`projects/memory-chat/` — all provider/model/memory features carry over unchanged.

## What's new
- Sessions are named and stored in a local SQLite database
- On startup, user can select an existing session or create a new one
- Chat history is written to the DB on every message
- Reloading or restarting the app restores the selected session

## Inherited features
- Streamlit UI
- Provider/model selection (OpenAI, Anthropic, Google — premium/default/lite tiers)
- Memory dropdown: 1–10 user/assistant pairs kept in context

## Out of scope
- Multi-user / auth
- Cloud storage
- Session sharing or export

## Success criteria
- Send messages, restart app, reopen session — history is intact
- Multiple named sessions can coexist
- New session starts with empty history
