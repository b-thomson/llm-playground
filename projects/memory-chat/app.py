import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / "../../.env")

PROVIDERS = {
    "OpenAI": {
        "default": "gpt-4o-mini",
        "premium": "gpt-4o",
        "lite": "gpt-3.5-turbo",
    },
    "Anthropic": {
        "default": "claude-sonnet-4-6",
        "premium": "claude-opus-4-7",
        "lite": "claude-haiku-4-5-20251001",
    },
    "Google": {
        "default": "gemini-2.5-flash",
        "premium": "gemini-2.5-pro",
        "lite": "gemini-2.0-flash-lite",
    },
}

TIER_LABELS = {
    "default": "Default (best value)",
    "premium": "Premium",
    "lite": "Lite (fastest/cheapest)",
}


def model_options(provider: str) -> list[str]:
    return list(PROVIDERS[provider].values())


def model_labels(provider: str) -> list[str]:
    return [f"{TIER_LABELS[t]} — {m}" for t, m in PROVIDERS[provider].items()]


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


# --- Init state ---

if "messages" not in st.session_state:
    st.session_state.messages = []

if "provider" not in st.session_state:
    st.session_state.provider = "OpenAI"

if "model" not in st.session_state:
    st.session_state.model = PROVIDERS["OpenAI"]["default"]

if "memory" not in st.session_state:
    st.session_state.memory = 5


def on_provider_change():
    provider = st.session_state["provider_select"]
    st.session_state.provider = provider
    st.session_state.model = PROVIDERS[provider]["default"]


def on_model_change():
    provider = st.session_state.provider
    selected_label = st.session_state["model_select"]
    labels = model_labels(provider)
    models = model_options(provider)
    idx = labels.index(selected_label)
    st.session_state.model = models[idx]


# --- Layout ---

st.title("memory-chat")

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
    provider = st.session_state.provider
    labels = model_labels(provider)
    models = model_options(provider)
    current_model = st.session_state.model
    current_idx = models.index(current_model) if current_model in models else 0
    st.selectbox(
        "Model",
        options=labels,
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

if prompt := st.chat_input("Say something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
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