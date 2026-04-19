import os
import sqlite3
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / "../../.env")

DB_PATH = Path(__file__).parent / "chat.db"

PROVIDERS = {
    "OpenAI": {
        "premium": "gpt-4o",
        "default": "gpt-4o-mini",
        "lite": "gpt-3.5-turbo",
    },
    "Anthropic": {
        "premium": "claude-opus-4-7",
        "default": "claude-sonnet-4-6",
        "lite": "claude-haiku-4-5-20251001",
    },
    "Google": {
        "premium": "gemini-2.5-pro",
        "default": "gemini-2.5-flash",
        "lite": "gemini-2.0-flash-lite",
    },
}


def model_options(provider: str) -> list[str]:
    return list(PROVIDERS[provider].values())


# --- DB helpers ---

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
    return [{"role": r, "content": c} for r, c in rows]


def save_message(session_id: int, role: str, content: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content),
        )


# --- LLM ---

def get_response(messages: list[dict], provider: str, model: str) -> str:
    match provider:
        case "OpenAI":
            from openai import OpenAI
            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            resp = client.chat.completions.create(model=model, messages=messages)
            return resp.choices[0].message.content

        case "Anthropic":
            from anthropic import Anthropic
            client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
            resp = client.messages.create(
                model=model,
                max_tokens=4096,
                messages=messages,
            )
            return resp.content[0].text

        case "Google":
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
            contents = [
                types.Content(
                    role="user" if m["role"] == "user" else "model",
                    parts=[types.Part(text=m["content"])],
                )
                for m in messages
            ]
            resp = client.models.generate_content(model=model, contents=contents)
            return resp.text

        case _:
            raise ValueError(f"Unknown provider: {provider}")


# --- Startup ---

init_db()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "provider" not in st.session_state:
    st.session_state.provider = "OpenAI"
if "model" not in st.session_state:
    st.session_state.model = PROVIDERS["OpenAI"]["default"]
if "memory" not in st.session_state:
    st.session_state.memory = 5
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "session_name" not in st.session_state:
    st.session_state.session_name = None


# --- Callbacks ---

def on_provider_change():
    provider = st.session_state["provider_select"]
    st.session_state.provider = provider
    st.session_state.model = PROVIDERS[provider]["default"]


def on_model_change():
    st.session_state.model = st.session_state["model_select"]


def on_session_change():
    selected = st.session_state["session_select"]
    sessions = get_sessions()
    for sid, name in sessions:
        if name == selected:
            st.session_state.session_id = sid
            st.session_state.session_name = name
            st.session_state.messages = load_messages(sid)
            break


# --- Layout ---

st.title("memory-chat-persistent")

# Session row
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
    new_name = st.text_input("Session name", key="new_session_name")
    if st.button("Create"):
        if new_name.strip():
            sid = create_session(new_name.strip())
            st.session_state.session_id = sid
            st.session_state.session_name = new_name.strip()
            st.session_state.messages = []
            st.session_state["_creating_session"] = False
            st.rerun()

# Provider/model/memory row
col1, col2, col3 = st.columns(3)

with col1:
    st.selectbox(
        "Provider",
        options=list(PROVIDERS.keys()),
        index=list(PROVIDERS.keys()).index(st.session_state.provider),
        key="provider_select",
        on_change=on_provider_change,
    )

with col2:
    models = model_options(st.session_state.provider)
    current_idx = models.index(st.session_state.model) if st.session_state.model in models else 1
    st.selectbox(
        "Model",
        options=models,
        index=current_idx,
        key="model_select",
        on_change=on_model_change,
    )

with col3:
    st.session_state.memory = st.selectbox(
        "Memory (pairs)",
        options=list(range(1, 11)),
        index=st.session_state.memory - 1,
    )

st.divider()

# --- Chat history ---

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Input ---

if st.session_state.session_id and (prompt := st.chat_input("Say something...")):
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_message(st.session_state.session_id, "user", prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    n_pairs = st.session_state.memory
    context = st.session_state.messages[-(n_pairs * 2):]

    with st.chat_message("assistant"):
        with st.spinner(""):
            try:
                reply = get_response(context, st.session_state.provider, st.session_state.model)
            except KeyError as e:
                reply = f"Missing API key: {e}. Add it to the root `.env`."
            except Exception as e:
                reply = f"Error: {e}"
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    save_message(st.session_state.session_id, "assistant", reply)
elif not st.session_state.session_id:
    st.chat_input("Create a session first...", disabled=True)