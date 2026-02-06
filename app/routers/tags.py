from fastapi import APIRouter, HTTPException, Query
from app.database import get_db
from app.models import Tag, TagsAdd, ThreadSummary
import math

router = APIRouter(tags=["tags"])


@router.get("/api/tags", response_model=list[Tag])
async def list_tags():
    db = await get_db()
    rows = await db.execute_fetchall("""
        SELECT tag_name AS name, COUNT(*) AS thread_count
        FROM thread_tags
        GROUP BY tag_name
        ORDER BY thread_count DESC, tag_name
    """)
    return [dict(r) for r in rows]


@router.post("/api/threads/{thread_id}/tags", status_code=201)
async def add_tags(thread_id: int, body: TagsAdd):
    db = await get_db()
    thread = await db.execute_fetchall("SELECT id FROM threads WHERE id = ?", (thread_id,))
    if not thread:
        raise HTTPException(404, "Thread not found")

    added = []
    for tag in body.tags:
        tag = tag.strip().lower()
        if tag:
            await db.execute(
                "INSERT OR IGNORE INTO thread_tags (thread_id, tag_name) VALUES (?, ?)",
                (thread_id, tag),
            )
            added.append(tag)
    await db.commit()

    rows = await db.execute_fetchall(
        "SELECT tag_name FROM thread_tags WHERE thread_id = ? ORDER BY tag_name",
        (thread_id,),
    )
    return {"thread_id": thread_id, "tags": [r["tag_name"] for r in rows]}


@router.delete("/api/threads/{thread_id}/tags/{tag_name}", status_code=204)
async def remove_tag(thread_id: int, tag_name: str):
    db = await get_db()
    existing = await db.execute_fetchall(
        "SELECT * FROM thread_tags WHERE thread_id = ? AND tag_name = ?",
        (thread_id, tag_name),
    )
    if not existing:
        raise HTTPException(404, "Tag not found on thread")

    await db.execute(
        "DELETE FROM thread_tags WHERE thread_id = ? AND tag_name = ?",
        (thread_id, tag_name),
    )
    await db.commit()


@router.get("/api/tags/{tag_name}/threads")
async def get_threads_by_tag(
    tag_name: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    db = await get_db()

    count_row = await db.execute_fetchall("""
        SELECT COUNT(*) AS total FROM thread_tags WHERE tag_name = ?
    """, (tag_name,))
    total = count_row[0]["total"]
    if total == 0:
        raise HTTPException(404, "Tag not found")

    total_pages = max(1, math.ceil(total / page_size))
    offset = (page - 1) * page_size

    rows = await db.execute_fetchall("""
        SELECT t.*, COALESCE(p.cnt, 0) AS post_count
        FROM threads t
        JOIN thread_tags tt ON tt.thread_id = t.id
        LEFT JOIN (SELECT thread_id, COUNT(*) AS cnt FROM posts GROUP BY thread_id) p
            ON p.thread_id = t.id
        WHERE tt.tag_name = ?
        ORDER BY t.created_at DESC
        LIMIT ? OFFSET ?
    """, (tag_name, page_size, offset))

    items = []
    for r in rows:
        d = dict(r)
        d["is_pinned"] = bool(d["is_pinned"])
        d["is_locked"] = bool(d["is_locked"])
        tag_rows = await db.execute_fetchall(
            "SELECT tag_name FROM thread_tags WHERE thread_id = ? ORDER BY tag_name",
            (d["id"],),
        )
        d["tags"] = [tr["tag_name"] for tr in tag_rows]
        items.append(d)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
