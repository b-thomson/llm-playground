# PRD — Context Inspector
_Status: stub / not started_

## Extends
memory-chat-persistent — see `../memory-chat-persistent/PRD.md` for base architecture. This project adds an inspection layer on top; all existing chat + memory functionality is inherited.

## Problem
LLM API interactions are a black box from the UI. Tool calls, token counts, message roles, and multi-turn context accumulation are invisible — making it hard to understand why a model behaves the way it does, or what's actually being sent and received.

## Goal
Add a real-time inspection panel to the existing chat app that exposes the full raw JSON exchange for every turn — request payload, response payload, tool use blocks, tool results, and token counts — in a readable, expandable UI.

## What Gets Inspected
- Full message array sent to the API each turn (role, content blocks)
- Raw API response (stop reason, usage, content)
- Tool use blocks — name, input JSON
- Tool results — content returned to the model
- Token counts — input, output, cache read/write if applicable
- Running context window size across the conversation

## UI
- Streamlit sidebar or collapsible panel alongside the chat
- One expandable section per turn
- Colour-coded by role (user / assistant / tool)
- Raw JSON view + summary view toggle (summary = just role + token count + tool names)

## Out of Scope
- Modifying or replaying requests
- Diffing across conversations
- Support for non-Anthropic providers in the inspector (Anthropic-first for now)

## Why This Project
- Makes the theory of tool use, context windows, and caching tangible
- Directly useful for debugging agent behaviour in later projects
- Natural third step in the progression: ephemeral → persistent → transparent
