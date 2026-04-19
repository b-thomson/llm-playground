# llm-playground

Monorepo of small, self-contained AI experiments.

## Structure
```
llm-playground/
├── .env                  # Shared API keys (never commit)
├── .gitignore
├── CLAUDE.md
└── projects/
    └── memory-chat/      # Streamlit chat app with provider/model/memory selection
```

## Conventions
- Each project in `projects/<name>/` is independently runnable
- All projects share the root `.env` — load with `dotenv.load_dotenv("../../.env")` from project root
- Write a PRD and TECH_SPEC before building

## New Project Setup (overrides user defaults)
- This is a monorepo — follow the monorepo layout from user CLAUDE.md
- `uv init --no-vcs` inside `projects/<name>/`, not the repo root
- Shared `.env` lives at repo root — load with `dotenv.load_dotenv("../../.env")` from the project folder

## Running a project
```bash
cd projects/<name>
uv run streamlit run app.py   # for Streamlit projects
```