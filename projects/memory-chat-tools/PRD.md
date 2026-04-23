# PRD — memory-chat-tools
_Status: in progress_

## Extends
memory-chat-persistent — SQLite session persistence, session selector UI, configurable memory window.

## Problem
Chat with LLMs is inherently passive: the model can only work with what it already knows. Tool use (function calling) breaks that constraint — the model can act, not just respond. But seeing tool use in action requires a working example.

## Goal
Add real tool use to the persistent chat app using the Anthropic tool use API. The model can call a web search tool mid-conversation, process the results, and incorporate them into its response. The full agentic loop — request → tool call → result → final response — is handled server-side and surfaced in the UI.

## What It Does
- Single tool: `web_search` (via Tavily)
- Anthropic-only (tool use is the focus; multi-provider parity is out of scope)
- Agentic loop: model may call the tool multiple times before final response
- Tool calls visible in chat UI (inline "Searching: ..." info box)
- Full message history (including tool intermediaries) persisted to SQLite for context continuity
- SQLite session persistence from memory-chat-persistent retained

## Out of Scope
- Multiple tools
- Tool result editing or replay
- Non-Anthropic providers
- Streaming responses

## Why This Project
- Makes tool use tangible before adding the inspector layer
- Produces real tool call + result messages to inspect in the next project
- Natural fourth step: ephemeral → persistent → transparent → agentic
