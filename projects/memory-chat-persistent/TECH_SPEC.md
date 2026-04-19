# Tech Spec — memory-chat-persistent

## Builds on
`projects/memory-chat/` — see that project's TECH_SPEC for base architecture.

## What changes

### New dependency
- `sqlite3` — stdlib, no install needed

### Database
Single file `chat.db` in the project root (gitignored). Schema:

```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER REFERENCES sessions(id),
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### New state
| Key | Type | Description |
|---|---|---|
| `session_id` | `int` | Active session DB id |
| `session_name` | `str` | Display name |

### New UI elements
Session selector at the top (above provider/model row):
```
[Session v]  [+ New session]
```
- Dropdown lists existing sessions by name
- "New session" button prompts for a name and creates it

### DB helpers (added to app.py)
- `init_db()` — creates tables if they don't exist, called at startup
- `load_messages(session_id) -> list[dict]` — reads history from DB into session_state
- `save_message(session_id, role, content)` — appends a single message to DB

### Flow change
On message send: write to DB immediately after appending to `session_state.messages`.
On session switch: clear `session_state.messages`, load from DB for new session.

## What doesn't change
Provider/model config, API call routing, memory windowing, error handling — all identical to memory-chat.

## Files added to .gitignore
`chat.db`