import aiosqlite
import os

DB_PATH = os.environ.get("FORUM_DB_PATH", "forum.db")

_db: aiosqlite.Connection | None = None


async def get_db() -> aiosqlite.Connection:
    global _db
    if _db is None:
        _db = await aiosqlite.connect(DB_PATH)
        _db.row_factory = aiosqlite.Row
        await _db.execute("PRAGMA journal_mode=WAL")
        await _db.execute("PRAGMA foreign_keys=ON")
    return _db


async def close_db():
    global _db
    if _db is not None:
        await _db.close()
        _db = None


async def init_db():
    db = await get_db()

    await db.executescript("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS threads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            author_name TEXT NOT NULL,
            is_pinned INTEGER DEFAULT 0,
            is_locked INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id INTEGER NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
            author_name TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS reactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
            reaction_type TEXT NOT NULL CHECK(reaction_type IN ('upvote', 'downvote')),
            reactor_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(post_id, reactor_name, reaction_type)
        );

        CREATE TABLE IF NOT EXISTS thread_tags (
            thread_id INTEGER NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
            tag_name TEXT NOT NULL,
            PRIMARY KEY (thread_id, tag_name)
        );

        CREATE INDEX IF NOT EXISTS idx_threads_category ON threads(category_id);
        CREATE INDEX IF NOT EXISTS idx_posts_thread ON posts(thread_id);
        CREATE INDEX IF NOT EXISTS idx_reactions_post ON reactions(post_id);
        CREATE INDEX IF NOT EXISTS idx_thread_tags_tag ON thread_tags(tag_name);
    """)

    # Full-text search tables
    await db.executescript("""
        CREATE VIRTUAL TABLE IF NOT EXISTS threads_fts USING fts5(
            title, content, thread_id UNINDEXED
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS posts_fts USING fts5(
            content, post_id UNINDEXED
        );
    """)

    await db.commit()
