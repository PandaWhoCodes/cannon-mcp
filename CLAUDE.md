# Forum Backend

## Overview

A no-auth forum API built with FastAPI + SQLite (aiosqlite). Serves as a sample backend for frontend consumers to integrate against.

## Documentation

Detailed docs live in two locations — check both:
- `/CLAUDE.md` (this file) — top-level project context
- `/docs/` — detailed API reference, data model, and architecture docs

## Tech Stack

- **Framework:** FastAPI (Python)
- **Database:** SQLite via aiosqlite (stored as `forum.db`, gitignored)
- **Models:** Pydantic v2 for request/response validation
- **Search:** SQLite FTS5 for full-text search
- **Auth:** None — all endpoints are open

## Project Structure

```
app/
  main.py              # FastAPI app, CORS, lifespan, seed data
  database.py          # SQLite connection, schema init, FTS setup
  models.py            # All Pydantic request/response schemas
  routers/
    categories.py      # CRUD for forum categories
    threads.py         # Thread creation, listing, pinning, locking
    posts.py           # Post CRUD with reaction counts
    reactions.py       # Upvote/downvote on posts
    tags.py            # Tag management and browsing
    search.py          # Full-text search (FTS5)
    stats.py           # Forum stats and trending threads
requirements.txt       # Python dependencies
docs/                  # Detailed documentation
```

## Running the Server

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Server starts at `http://localhost:8000`. Interactive API docs at `/docs`.

The database auto-creates on first run with seed data (5 categories, 7 threads, 14 posts).

## Key Patterns

- **Database:** Single global aiosqlite connection with WAL mode and foreign keys enabled. `get_db()` returns the shared connection.
- **Pagination:** All list endpoints accept `page` and `page_size` query params. Return `{items, total, page, page_size, total_pages}`.
- **FTS:** Threads and posts are indexed in `threads_fts` / `posts_fts` virtual tables. FTS entries must be manually kept in sync on create/update/delete.
- **Seed data:** `seed_data()` runs on startup, only populates if the DB is empty.
- **CORS:** Wide open (`*` origins) for frontend development.

## Common Tasks

- **Add a new endpoint:** Create or edit a router in `app/routers/`, register it in `app/main.py` via `app.include_router()`.
- **Change the schema:** Edit `init_db()` in `app/database.py`. Delete `forum.db` to recreate from scratch.
- **Add seed data:** Edit `seed_data()` in `app/main.py`.
- **Modify validation:** Edit Pydantic models in `app/models.py`.
