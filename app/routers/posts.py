from fastapi import APIRouter, HTTPException, Query
from app.database import get_db
from app.models import Post, PostCreate, PostUpdate
import math

router = APIRouter(tags=["posts"])


async def _get_post_with_reactions(db, post_id: int) -> dict | None:
    rows = await db.execute_fetchall("""
        SELECT p.*,
            COALESCE(SUM(CASE WHEN r.reaction_type = 'upvote' THEN 1 ELSE 0 END), 0) AS upvotes,
            COALESCE(SUM(CASE WHEN r.reaction_type = 'downvote' THEN 1 ELSE 0 END), 0) AS downvotes
        FROM posts p
        LEFT JOIN reactions r ON r.post_id = p.id
        WHERE p.id = ?
        GROUP BY p.id
    """, (post_id,))
    if not rows:
        return None
    return dict(rows[0])


@router.get("/api/threads/{thread_id}/posts")
async def list_posts_in_thread(
    thread_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    db = await get_db()

    thread = await db.execute_fetchall("SELECT id, is_locked FROM threads WHERE id = ?", (thread_id,))
    if not thread:
        raise HTTPException(404, "Thread not found")

    count_row = await db.execute_fetchall(
        "SELECT COUNT(*) AS total FROM posts WHERE thread_id = ?", (thread_id,)
    )
    total = count_row[0]["total"]
    total_pages = max(1, math.ceil(total / page_size))
    offset = (page - 1) * page_size

    rows = await db.execute_fetchall("""
        SELECT p.*,
            COALESCE(SUM(CASE WHEN r.reaction_type = 'upvote' THEN 1 ELSE 0 END), 0) AS upvotes,
            COALESCE(SUM(CASE WHEN r.reaction_type = 'downvote' THEN 1 ELSE 0 END), 0) AS downvotes
        FROM posts p
        LEFT JOIN reactions r ON r.post_id = p.id
        WHERE p.thread_id = ?
        GROUP BY p.id
        ORDER BY p.created_at ASC
        LIMIT ? OFFSET ?
    """, (thread_id, page_size, offset))

    return {
        "items": [dict(r) for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "is_locked": bool(thread[0]["is_locked"]),
    }


@router.post("/api/posts", response_model=Post, status_code=201)
async def create_post(body: PostCreate):
    db = await get_db()

    thread = await db.execute_fetchall(
        "SELECT id, is_locked FROM threads WHERE id = ?", (body.thread_id,)
    )
    if not thread:
        raise HTTPException(404, "Thread not found")
    if thread[0]["is_locked"]:
        raise HTTPException(403, "Thread is locked")

    cursor = await db.execute(
        "INSERT INTO posts (thread_id, author_name, content) VALUES (?, ?, ?)",
        (body.thread_id, body.author_name, body.content),
    )
    post_id = cursor.lastrowid

    # Update thread updated_at
    await db.execute(
        "UPDATE threads SET updated_at = datetime('now') WHERE id = ?",
        (body.thread_id,),
    )

    # Update FTS
    await db.execute(
        "INSERT INTO posts_fts (post_id, content) VALUES (?, ?)",
        (post_id, body.content),
    )

    await db.commit()
    return await _get_post_with_reactions(db, post_id)


@router.get("/api/posts/{post_id}", response_model=Post)
async def get_post(post_id: int):
    db = await get_db()
    result = await _get_post_with_reactions(db, post_id)
    if not result:
        raise HTTPException(404, "Post not found")
    return result


@router.put("/api/posts/{post_id}", response_model=Post)
async def update_post(post_id: int, body: PostUpdate):
    db = await get_db()
    existing = await db.execute_fetchall("SELECT * FROM posts WHERE id = ?", (post_id,))
    if not existing:
        raise HTTPException(404, "Post not found")

    await db.execute(
        "UPDATE posts SET content = ?, updated_at = datetime('now') WHERE id = ?",
        (body.content, post_id),
    )

    # Update FTS
    await db.execute("DELETE FROM posts_fts WHERE post_id = ?", (post_id,))
    await db.execute(
        "INSERT INTO posts_fts (post_id, content) VALUES (?, ?)",
        (post_id, body.content),
    )

    await db.commit()
    return await _get_post_with_reactions(db, post_id)


@router.delete("/api/posts/{post_id}", status_code=204)
async def delete_post(post_id: int):
    db = await get_db()
    existing = await db.execute_fetchall("SELECT * FROM posts WHERE id = ?", (post_id,))
    if not existing:
        raise HTTPException(404, "Post not found")

    await db.execute("DELETE FROM posts_fts WHERE post_id = ?", (post_id,))
    await db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    await db.commit()
