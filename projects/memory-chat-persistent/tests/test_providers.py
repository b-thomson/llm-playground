"""Smoke tests — verify each provider's API key is valid and returns a response."""
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / "../../../.env")

MESSAGES = [{"role": "user", "content": "Reply with the single word: ok"}]


def test_openai():
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resp = client.chat.completions.create(model="gpt-4o-mini", messages=MESSAGES)
    assert resp.choices[0].message.content.strip()


def test_anthropic():
    from anthropic import Anthropic
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    resp = client.messages.create(model="claude-haiku-4-5-20251001", max_tokens=16, messages=MESSAGES)
    assert resp.content[0].text.strip()


def test_google():
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    contents = [types.Content(role="user", parts=[types.Part(text=MESSAGES[0]["content"])])]
    resp = client.models.generate_content(model="gemini-2.5-flash", contents=contents)
    assert resp.text.strip()