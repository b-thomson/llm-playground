import json
import os
import sqlite3
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / "../../.env")

DB_PATH = Path(__file__).parent / "chat.db"

MODELS = {
    "premium": "claude-opus-4-7",
    "default": "claude-sonnet-4-6",
    "lite": "claude-haiku-4-5-20251001",
}

TOOLS = [
    {
        "name": "web_search",
        "description": (
            "Search the web for current information. Use when asked about recent events, "
            "live data, or anything you might not know with confidence."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"},
            },
            "required": ["query"],
        },
    }
]

st.set_page_config(layout="wide", page_title="context-inspector")


# --- DB ---

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER REFERENCES sessions(id),
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)


def get_sessions() -> list[tuple[int, str]]:
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("SELECT id, name FROM sessions ORDER BY created_at DESC").fetchall()


def create_session(name: str) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("INSERT INTO sessions (name) VALUES (?)", (name,))
        return cur.lastrowid


def load_messages(session_id: int) -> list[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at",
            (session_id,),
        ).fetchall()
    return [{"role": r, "content": json.loads(c)} for r, c in rows]


def save_message(session_id: int, role: str, content):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, json.dumps(content)),
        )


# --- Tools ---

def execute_tool(name: str, tool_input: dict) -> str:
    if name == "web_search":
        from tavily import TavilyClient
        client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
        result = client.search(query=tool_input["query"], max_results=3)
        parts = [
            f"**{r['title']}**\n{r['url']}\n{r['content']}"
            for r in result.get("results", [])
        ]
        return "\n\n".join(parts) or "No results found."
    raise ValueError(f"Unknown tool: {name}")


# --- Agent loop ---

def run_agent(messages: list[dict], model: str) -> tuple[str, list[dict]]:
    from anthropic import Anthropic
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    working = list(messages)
    intermediates = []

    while True:
        resp = client.messages.create(
            model=model,
            max_tokens=4096,
            tools=TOOLS,
            messages=working,
            cache_control={"type": "ephemeral"},
        )

        if resp.stop_reason == "end_turn":
            text = next((b.text for b in resp.content if b.type == "text"), "")
            return text, intermediates

        if resp.stop_reason == "tool_use":
            assistant_content = []
            for b in resp.content:
                if b.type == "text":
                    assistant_content.append({"type": "text", "text": b.text})
                elif b.type == "tool_use":
                    assistant_content.append({
                        "type": "tool_use",
                        "id": b.id,
                        "name": b.name,
                        "input": b.input,
                    })

            tool_results = []
            for b in resp.content:
                if b.type == "tool_use":
                    result = execute_tool(b.name, b.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": b.id,
                        "content": result,
                    })

            assistant_msg = {"role": "assistant", "content": assistant_content}
            user_msg = {"role": "user", "content": tool_results}

            working.append(assistant_msg)
            working.append(user_msg)
            intermediates.append(assistant_msg)
            intermediates.append(user_msg)


# --- Inspector helpers ---

def group_into_turns(messages: list[dict]) -> list[list[dict]]:
    turns: list[list[dict]] = []
    current: list[dict] = []
    for msg in messages:
        is_user_text = msg["role"] == "user" and isinstance(msg["content"], str)
        if is_user_text and current:
            turns.append(current)
            current = []
        current.append(msg)
    if current:
        turns.append(current)
    return turns


def turn_label(i: int, turn: list[dict]) -> str:
    text = turn[0]["content"]
    preview = text[:55].rstrip() + ("…" if len(text) > 55 else "")
    return f"Turn {i} — {preview}"


def role_badge(msg: dict) -> str:
    if msg["role"] == "user":
        return "user → assistant"
    return "assistant → user"


# --- Chat render ---

def render_chat_message(msg: dict):
    role = msg["role"]
    content = msg["content"]
    if isinstance(content, str):
        with st.chat_message(role):
            st.markdown(content)
        return
    for block in content:
        if block.get("type") == "text" and block.get("text"):
            with st.chat_message(role):
                st.markdown(block["text"])
        elif block.get("type") == "tool_use":
            with st.chat_message("assistant"):
                st.info(f"Searched: *{block['input'].get('query', '')}*")


# --- Startup ---

init_db()

st.markdown(
    "<style>div[data-testid='stCodeBlock'] pre { white-space: pre-wrap !important; overflow-x: unset !important; }</style>",
    unsafe_allow_html=True,
)

for key, default in [
    ("messages", []),
    ("model", MODELS["default"]),
    ("session_id", None),
    ("session_name", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# --- Callbacks ---

def on_model_change():
    st.session_state.model = st.session_state["model_select"]


def on_session_change():
    selected = st.session_state["session_select"]
    for sid, name in get_sessions():
        if name == selected:
            st.session_state.session_id = sid
            st.session_state.session_name = name
            st.session_state.messages = load_messages(sid)
            break


# --- Layout ---

st.title("context-inspector")

sessions = get_sessions()
session_names = [name for _, name in sessions]

col_sess, col_new = st.columns([4, 1])

with col_sess:
    if session_names:
        if st.session_state.session_id is None:
            st.session_state.session_id = sessions[0][0]
            st.session_state.session_name = sessions[0][1]
            st.session_state.messages = load_messages(sessions[0][0])
        current_name = st.session_state.session_name
        st.selectbox(
            "Session",
            options=session_names,
            index=session_names.index(current_name) if current_name in session_names else 0,
            key="session_select",
            on_change=on_session_change,
        )
    else:
        st.info("No sessions yet — create one to start.")

with col_new:
    st.write("")
    st.write("")
    if st.button("+ New"):
        st.session_state["_creating_session"] = True

if st.session_state.get("_creating_session"):
    with st.form("new_session_form", clear_on_submit=True):
        new_name = st.text_input("Session name")
        if st.form_submit_button("Create") and new_name.strip():
            sid = create_session(new_name.strip())
            st.session_state.session_id = sid
            st.session_state.session_name = new_name.strip()
            st.session_state.messages = []
            st.session_state["_creating_session"] = False
            st.rerun()

col_model, _ = st.columns([1, 2])
with col_model:
    st.selectbox(
        "Model",
        options=list(MODELS.values()),
        index=list(MODELS.values()).index(st.session_state.model),
        key="model_select",
        on_change=on_model_change,
    )

st.divider()

# Chat
for msg in st.session_state.messages:
    render_chat_message(msg)

if st.session_state.session_id and (prompt := st.chat_input("Ask anything...")):
    user_msg = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_msg)
    save_message(st.session_state.session_id, "user", prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner(""):
        try:
            reply, intermediates = run_agent(st.session_state.messages, st.session_state.model)
        except KeyError as e:
            reply = f"Missing API key: {e}. Add it to the root `.env`."
            intermediates = []
        except Exception as e:
            reply = f"Error: {e}"
            intermediates = []

    for msg in intermediates:
        render_chat_message(msg)
        save_message(st.session_state.session_id, msg["role"], msg["content"])
        st.session_state.messages.append(msg)

    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    save_message(st.session_state.session_id, "assistant", reply)

elif not st.session_state.session_id:
    st.chat_input("Create a session first...", disabled=True)

# Inspector sidebar — runs after chat processing so messages are up to date
turns = group_into_turns(st.session_state.messages)
with st.sidebar:
    st.header("Inspector")
    if turns:
        st.caption(f"{len(turns)} turn{'s' if len(turns) != 1 else ''} · {len(st.session_state.messages)} message{'s' if len(st.session_state.messages) != 1 else ''}")
        st.divider()
        cumulative = []
        for i, turn in enumerate(turns, 1):
            with st.expander(turn_label(i, turn), expanded=False):
                if cumulative:
                    st.caption(f"↑ {len(cumulative)} prior message{'s' if len(cumulative) != 1 else ''} in context")
                    st.divider()
                for msg in turn:
                    st.markdown(f"**`{role_badge(msg)}`**")
                    st.code(json.dumps(msg["content"], indent=2, ensure_ascii=False), language="json")
                    st.write("")
            cumulative.extend(turn)
    else:
        st.caption("No turns yet.")
