from fastapi import APIRouter, HTTPException, Query
from app.database import get_db
from app.models import ThreadCreate, ThreadUpdate, ThreadSummary, ThreadDetail
import math

router = APIRouter(tags=["threads"])


async def _get_thread_tags(db, thread_id: int) -> list[str]:
    rows = await db.execute_fetchall(
        "SELECT tag_name FROM thread_tags WHERE thread_id = ? ORDER BY tag_name",
        (thread_id,),
    )
    return [r["tag_name"] for r in rows]


@router.get("/api/categories/{category_id}/threads")
async def list_threads_in_category(
    category_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort: str = Query("created_at", pattern="^(created_at|updated_at|post_count)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
):
    db = await get_db()

    # Verify category exists
    cat = await db.execute_fetchall("SELECT id FROM categories WHERE id = ?", (category_id,))
    if not cat:
        raise HTTPException(404, "Category not found")

    # Count total
    count_row = await db.execute_fetchall(
        "SELECT COUNT(*) AS total FROM threads WHERE category_id = ?", (category_id,)
    )
    total = count_row[0]["total"]
    total_pages = max(1, math.ceil(total / page_size))
    offset = (page - 1) * page_size

    if sort == "post_count":
        order_clause = f"post_count {order}"
    else:
        order_clause = f"t.{sort} {order}"

    rows = await db.execute_fetchall(f"""
        SELECT t.*, COALESCE(p.cnt, 0) AS post_count
        FROM threads t
        LEFT JOIN (SELECT thread_id, COUNT(*) AS cnt FROM posts GROUP BY thread_id) p
            ON p.thread_id = t.id
        WHERE t.category_id = ?
        ORDER BY t.is_pinned DESC, {order_clause}
        LIMIT ? OFFSET ?
    """, (category_id, page_size, offset))

    items = []
    for r in rows:
        d = dict(r)
        d["is_pinned"] = bool(d["is_pinned"])
        d["is_locked"] = bool(d["is_locked"])
        d["tags"] = await _get_thread_tags(db, d["id"])
        items.append(d)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.post("/api/threads", response_model=ThreadDetail, status_code=201)
async def create_thread(body: ThreadCreate):
    db = await get_db()

    # Verify category
    cat = await db.execute_fetchall("SELECT * FROM categories WHERE id = ?", (body.category_id,))
    if not cat:
        raise HTTPException(404, "Category not found")

    cursor = await db.execute(
        "INSERT INTO threads (category_id, title, author_name) VALUES (?, ?, ?)",
        (body.category_id, body.title, body.author_name),
    )
    thread_id = cursor.lastrowid

    # Create first post
    await db.execute(
        "INSERT INTO posts (thread_id, author_name, content) VALUES (?, ?, ?)",
        (thread_id, body.author_name, body.content),
    )

    # Add tags
    for tag in body.tags:
        tag = tag.strip().lower()
        if tag:
            await db.execute(
                "INSERT OR IGNORE INTO thread_tags (thread_id, tag_name) VALUES (?, ?)",
                (thread_id, tag),
            )

    # Update FTS
    await db.execute(
        "INSERT INTO threads_fts (thread_id, title, content) VALUES (?, ?, ?)",
        (thread_id, body.title, body.content),
    )
    await db.execute(
        "INSERT INTO posts_fts (post_id, content) VALUES (?, ?)",
        (cursor.lastrowid, body.content),
    )

    await db.commit()

    rows = await db.execute_fetchall("""
        SELECT t.*, c.name AS category_name, COALESCE(p.cnt, 0) AS post_count
        FROM threads t
        JOIN categories c ON c.id = t.category_id
        LEFT JOIN (SELECT thread_id, COUNT(*) AS cnt FROM posts GROUP BY thread_id) p
            ON p.thread_id = t.id
        WHERE t.id = ?
    """, (thread_id,))
    d = dict(rows[0])
    d["is_pinned"] = bool(d["is_pinned"])
    d["is_locked"] = bool(d["is_locked"])
    d["tags"] = await _get_thread_tags(db, thread_id)
    return d


@router.get("/api/threads/{thread_id}", response_model=ThreadDetail)
async def get_thread(thread_id: int):
    db = await get_db()
    rows = await db.execute_fetchall("""
        SELECT t.*, c.name AS category_name, COALESCE(p.cnt, 0) AS post_count
        FROM threads t
        JOIN categories c ON c.id = t.category_id
        LEFT JOIN (SELECT thread_id, COUNT(*) AS cnt FROM posts GROUP BY thread_id) p
            ON p.thread_id = t.id
        WHERE t.id = ?
    """, (thread_id,))
    if not rows:
        raise HTTPException(404, "Thread not found")
    d = dict(rows[0])
    d["is_pinned"] = bool(d["is_pinned"])
    d["is_locked"] = bool(d["is_locked"])
    d["tags"] = await _get_thread_tags(db, thread_id)
    return d


@router.put("/api/threads/{thread_id}", response_model=ThreadDetail)
async def update_thread(thread_id: int, body: ThreadUpdate):
    db = await get_db()
    existing = await db.execute_fetchall("SELECT * FROM threads WHERE id = ?", (thread_id,))
    if not existing:
        raise HTTPException(404, "Thread not found")

    updates = {}
    if body.title is not None:
        updates["title"] = body.title
    if body.is_pinned is not None:
        updates["is_pinned"] = int(body.is_pinned)
    if body.is_locked is not None:
        updates["is_locked"] = int(body.is_locked)

    if updates:
        updates["updated_at"] = "datetime('now')"
        set_parts = []
        values = []
        for k, v in updates.items():
            if k == "updated_at":
                set_parts.append("updated_at = datetime('now')")
            else:
                set_parts.append(f"{k} = ?")
                values.append(v)
        values.append(thread_id)
        await db.execute(
            f"UPDATE threads SET {', '.join(set_parts)} WHERE id = ?", values
        )

        # Update FTS title if changed
        if body.title is not None:
            await db.execute(
                "UPDATE threads_fts SET title = ? WHERE thread_id = ?",
                (body.title, thread_id),
            )

        await db.commit()

    rows = await db.execute_fetchall("""
        SELECT t.*, c.name AS category_name, COALESCE(p.cnt, 0) AS post_count
        FROM threads t
        JOIN categories c ON c.id = t.category_id
        LEFT JOIN (SELECT thread_id, COUNT(*) AS cnt FROM posts GROUP BY thread_id) p
            ON p.thread_id = t.id
        WHERE t.id = ?
    """, (thread_id,))
    d = dict(rows[0])
    d["is_pinned"] = bool(d["is_pinned"])
    d["is_locked"] = bool(d["is_locked"])
    d["tags"] = await _get_thread_tags(db, thread_id)
    return d


@router.delete("/api/threads/{thread_id}", status_code=204)
async def delete_thread(thread_id: int):
    db = await get_db()
    existing = await db.execute_fetchall("SELECT * FROM threads WHERE id = ?", (thread_id,))
    if not existing:
        raise HTTPException(404, "Thread not found")

    # Clean up FTS
    await db.execute("DELETE FROM threads_fts WHERE thread_id = ?", (thread_id,))
    posts = await db.execute_fetchall("SELECT id FROM posts WHERE thread_id = ?", (thread_id,))
    for p in posts:
        await db.execute("DELETE FROM posts_fts WHERE post_id = ?", (p["id"],))

    await db.execute("DELETE FROM threads WHERE id = ?", (thread_id,))
    await db.commit()
