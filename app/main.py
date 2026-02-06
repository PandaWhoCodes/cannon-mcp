from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db, close_db, get_db
from app.routers import categories, threads, posts, reactions, tags, search, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_data()
    yield
    await close_db()


app = FastAPI(
    title="Forum API",
    description="A no-auth forum backend with categories, threads, posts, reactions, tags, search, and stats.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories.router)
app.include_router(threads.router)
app.include_router(posts.router)
app.include_router(reactions.router)
app.include_router(tags.router)
app.include_router(search.router)
app.include_router(stats.router)


@app.get("/")
async def root():
    return {
        "name": "Forum API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "categories": "/api/categories",
            "threads": "/api/threads/{id}",
            "posts": "/api/posts/{id}",
            "tags": "/api/tags",
            "search": "/api/search?q=...",
            "stats": "/api/stats",
            "trending": "/api/stats/trending",
        },
    }


@app.get("/api/health")
async def health():
    db = await get_db()
    row = await db.execute_fetchall("SELECT 1 AS ok")
    return {"status": "healthy", "db": bool(row)}


async def seed_data():
    """Seed initial data if the database is empty."""
    db = await get_db()
    count = await db.execute_fetchall("SELECT COUNT(*) AS c FROM categories")
    if count[0]["c"] > 0:
        return

    # Categories
    categories_data = [
        ("General Discussion", "Talk about anything and everything"),
        ("Technology", "Programming, gadgets, and tech news"),
        ("Gaming", "Video games, board games, and esports"),
        ("Science", "Scientific discoveries and discussions"),
        ("Creative Corner", "Share your art, writing, and music"),
    ]
    for name, desc in categories_data:
        await db.execute(
            "INSERT INTO categories (name, description) VALUES (?, ?)", (name, desc)
        )

    # Threads with posts
    threads_data = [
        (1, "Welcome to the forum!", "admin", "Welcome everyone! Feel free to introduce yourselves and get to know the community.", ["welcome", "introduction"]),
        (1, "Forum rules and guidelines", "admin", "Please be respectful to all members. No spam, no harassment. Keep discussions civil and constructive.", ["rules", "meta"]),
        (2, "Best programming languages in 2026", "techie42", "What are your favorite programming languages this year? I've been really enjoying Rust and Python.", ["programming", "languages"]),
        (2, "Building APIs with FastAPI", "pythonista", "FastAPI has been amazing for building REST APIs. The auto-generated docs are a game changer!", ["python", "fastapi", "api"]),
        (3, "What are you playing right now?", "gamer_one", "Just started Elden Ring 2. The open world is even more incredible than the first. What about you all?", ["games", "current"]),
        (4, "James Webb latest discoveries", "stargazer", "The latest images from JWST are absolutely mind-blowing. Anyone else following the recent exoplanet discoveries?", ["space", "astronomy"]),
        (5, "Share your latest project", "creator", "I just finished a watercolor painting of a sunset. Would love to see what everyone else has been working on!", ["projects", "sharing"]),
    ]

    for cat_id, title, author, content, thread_tags in threads_data:
        cursor = await db.execute(
            "INSERT INTO threads (category_id, title, author_name) VALUES (?, ?, ?)",
            (cat_id, title, author),
        )
        thread_id = cursor.lastrowid

        post_cursor = await db.execute(
            "INSERT INTO posts (thread_id, author_name, content) VALUES (?, ?, ?)",
            (thread_id, author, content),
        )
        post_id = post_cursor.lastrowid

        for tag in thread_tags:
            await db.execute(
                "INSERT INTO thread_tags (thread_id, tag_name) VALUES (?, ?)",
                (thread_id, tag),
            )

        await db.execute(
            "INSERT INTO threads_fts (thread_id, title, content) VALUES (?, ?, ?)",
            (thread_id, title, content),
        )
        await db.execute(
            "INSERT INTO posts_fts (post_id, content) VALUES (?, ?)",
            (post_id, content),
        )

    # Add some replies
    replies = [
        (1, "user123", "Hi everyone! Glad to be here. Looking forward to great discussions!"),
        (1, "newbie_dev", "Hello! I'm new to programming and excited to learn from you all."),
        (3, "rust_fan", "Rust all the way! The borrow checker saved me from so many bugs."),
        (3, "js_lover", "TypeScript has been incredible. The type system keeps getting better."),
        (4, "backend_dev", "The dependency injection in FastAPI is so clean. Love using it with SQLAlchemy."),
        (5, "retro_gamer", "I'm replaying Zelda TOTK. The ultrahand builds are addictive!"),
        (6, "space_nerd", "The exoplanet data has been fascinating. Some candidates for habitable zones!"),
    ]

    for thread_id, author, content in replies:
        post_cursor = await db.execute(
            "INSERT INTO posts (thread_id, author_name, content) VALUES (?, ?, ?)",
            (thread_id, author, content),
        )
        await db.execute(
            "INSERT INTO posts_fts (post_id, content) VALUES (?, ?)",
            (post_cursor.lastrowid, content),
        )

    # Add some reactions
    reaction_data = [
        (1, "upvote", "user123"),
        (1, "upvote", "newbie_dev"),
        (2, "upvote", "user123"),
        (3, "upvote", "rust_fan"),
        (3, "upvote", "js_lover"),
        (4, "upvote", "backend_dev"),
        (5, "downvote", "retro_gamer"),
        (6, "upvote", "space_nerd"),
        (6, "upvote", "techie42"),
    ]

    for post_id, rtype, reactor in reaction_data:
        await db.execute(
            "INSERT INTO reactions (post_id, reaction_type, reactor_name) VALUES (?, ?, ?)",
            (post_id, rtype, reactor),
        )

    await db.commit()
