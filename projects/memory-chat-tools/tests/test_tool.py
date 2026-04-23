"""Smoke tests — verify API keys and tool connectivity."""
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / "../../../.env")


def test_anthropic_responds():
    from anthropic import Anthropic
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=32,
        messages=[{"role": "user", "content": "Reply with the word OK only."}],
    )
    assert resp.content[0].text.strip()


def test_anthropic_tool_use():
    """Verify the model can invoke a tool and we get a tool_use stop reason."""
    from anthropic import Anthropic
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        tools=[{
            "name": "web_search",
            "description": "Search the web.",
            "input_schema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        }],
        messages=[{"role": "user", "content": "Search the web for today's date."}],
    )
    assert resp.stop_reason == "tool_use"
    tool_block = next(b for b in resp.content if b.type == "tool_use")
    assert tool_block.name == "web_search"
    assert "query" in tool_block.input


def test_tavily_search():
    from tavily import TavilyClient
    client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    result = client.search(query="Python programming language", max_results=1)
    assert result.get("results")
    assert result["results"][0].get("content")