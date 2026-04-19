# Tech Spec — memory-chat

## Stack
- **UI**: Streamlit
- **LLM providers**: OpenAI SDK, Anthropic SDK, Google GenerativeAI SDK
- **Config**: python-dotenv, root `.env` at `../../.env`
- **Runtime**: Python 3.12, uv

## File structure
```
projects/memory-chat/
├── app.py           # Streamlit app — all logic lives here (single file)
├── pyproject.toml
├── PRD.md
├── TECH_SPEC.md
└── .venv/
```

## State (Streamlit session_state)
| Key | Type | Description |
|---|---|---|
| `messages` | `list[dict]` | Full chat history: `{role, content}` |
| `provider` | `str` | Selected provider key |
| `model` | `str` | Selected model ID |
| `memory` | `int` | N pairs to keep in context (1–10) |

## Provider/model config
Defined as a static dict in `app.py`. Each provider has `default`, `premium`, `lite` keys mapping to model IDs. Switching provider resets model to that provider's default via an `on_change` callback.

## Memory mechanics
When building the messages list for an API call, slice the last `N * 2` messages from `st.session_state.messages`. The system prompt (if any) is always prepended.

No system prompt in v1 — keep it simple.

## API call routing
Single `get_response(messages, provider, model) -> str` function with a match/case on provider:
- `openai`: `openai.OpenAI().chat.completions.create()`
- `anthropic`: `anthropic.Anthropic().messages.create()`
- `google`: `genai.GenerativeModel(model).generate_content()`

Each branch normalises the messages list to the provider's expected format.

## Environment variables
Loaded from `../../.env` relative to app.py:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`

Missing keys fail loudly at call time (not startup) — allows running the app without all keys set.

## Streamlit layout
```
[Provider v] [Model v] [Memory: N pairs v]
------------------------------------------
<chat history — user/assistant bubbles>
------------------------------------------
[chat_input]
```
Controls in a single `st.columns(3)` row at the top. Chat history rendered with `st.chat_message`. Input via `st.chat_input` (sticky footer).

## Error handling
Wrap API call in try/except; display error inline as an assistant message. No retries in v1.