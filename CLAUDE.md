# llm-playground

Monorepo of small, self-contained AI experiments.

## Structure
```
llm-playground/
├── .env                  # Shared API keys (never commit)
├── .gitignore
├── CLAUDE.md
└── projects/
    ├── memory-chat/             # Streamlit chat app with provider/model/memory selection
    ├── memory-chat-persistent/  # Extends memory-chat with SQLite session persistence
    ├── memory-chat-tools/       # Adds Anthropic tool use (web search via Tavily), agentic loop
    └── context-inspector/       # Read-only inspector for memory-chat-tools sessions (sidebar JSON view)
```

## Conventions
- Each project in `projects/<name>/` is independently runnable
- All projects share the root `.env` — load with `dotenv.load_dotenv("../../.env")` from project root
- Write a PRD and TECH_SPEC before building
- No per-project README — CLAUDE.md covers internal docs, root README covers the portfolio view

## New Project Setup (overrides user defaults)
- This is a monorepo — follow the monorepo layout from user CLAUDE.md
- `uv init --vcs none` inside `projects/<name>/`, not the repo root (flag changed: `--vcs none` not `--no-vcs`)
- Shared `.env` lives at repo root — load with `dotenv.load_dotenv("../../.env")` from the project folder

## Running a project
```bash
cd projects/<name>
uv run streamlit run app.py   # for Streamlit projects
```