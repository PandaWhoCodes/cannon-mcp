# Architecture

## Overview

Single-process FastAPI application with an embedded SQLite database. No external services, no auth, no message queues. Designed as a sample backend for frontend development.

## Request Flow

```
Client (browser/curl)
  │
  ▼
FastAPI (CORS middleware)
  │
  ▼
Router (categories/threads/posts/reactions/tags/search/stats)
  │
  ▼
aiosqlite (async SQLite connection)
  │
  ▼
forum.db (SQLite file, WAL mode)
```

## Key Design Decisions

### Single DB Connection

A single shared `aiosqlite.Connection` is used for the lifetime of the app. This avoids connection pool overhead for SQLite (which serializes writes anyway). The connection is created lazily on first `get_db()` call and closed on shutdown.

### WAL Mode

SQLite is configured with `PRAGMA journal_mode=WAL` for better concurrent read performance. Writes are still serialized.

### Foreign Keys

`PRAGMA foreign_keys=ON` is set on connection. All FK relationships use `ON DELETE CASCADE` so deleting a parent cleans up children.

### FTS5 Full-Text Search

SQLite's FTS5 extension provides full-text search on thread titles and post content. FTS tables are separate virtual tables that must be manually kept in sync with the source data.

### No ORM

Raw SQL via aiosqlite for simplicity and transparency. Pydantic handles serialization/validation at the API boundary.

### Seed Data on Startup

The `seed_data()` function in `main.py` populates the database with sample data if empty. This runs every time the server starts, but is a no-op if data already exists.

## CORS

Configured with `allow_origins=["*"]` for maximum flexibility during frontend development. Tighten this for production.

## Error Handling

- 404 for missing resources
- 400 for validation errors (Pydantic) and constraint violations
- 403 for posting to locked threads
- 409 for duplicate reactions
