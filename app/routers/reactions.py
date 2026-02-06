from fastapi import APIRouter, HTTPException
from app.database import get_db
from app.models import Reaction, ReactionCreate

router = APIRouter(tags=["reactions"])


@router.post("/api/posts/{post_id}/reactions", response_model=Reaction, status_code=201)
async def add_reaction(post_id: int, body: ReactionCreate):
    db = await get_db()

    post = await db.execute_fetchall("SELECT id FROM posts WHERE id = ?", (post_id,))
    if not post:
        raise HTTPException(404, "Post not found")

    try:
        cursor = await db.execute(
            "INSERT INTO reactions (post_id, reaction_type, reactor_name) VALUES (?, ?, ?)",
            (post_id, body.reaction_type, body.reactor_name),
        )
        await db.commit()
    except Exception:
        raise HTTPException(409, "Reaction already exists")

    rows = await db.execute_fetchall(
        "SELECT * FROM reactions WHERE id = ?", (cursor.lastrowid,)
    )
    return dict(rows[0])


@router.delete("/api/posts/{post_id}/reactions/{reaction_type}", status_code=204)
async def remove_reaction(post_id: int, reaction_type: str, reactor_name: str):
    db = await get_db()
    existing = await db.execute_fetchall(
        "SELECT id FROM reactions WHERE post_id = ? AND reaction_type = ? AND reactor_name = ?",
        (post_id, reaction_type, reactor_name),
    )
    if not existing:
        raise HTTPException(404, "Reaction not found")

    await db.execute(
        "DELETE FROM reactions WHERE post_id = ? AND reaction_type = ? AND reactor_name = ?",
        (post_id, reaction_type, reactor_name),
    )
    await db.commit()


@router.get("/api/posts/{post_id}/reactions", response_model=list[Reaction])
async def list_reactions(post_id: int):
    db = await get_db()
    post = await db.execute_fetchall("SELECT id FROM posts WHERE id = ?", (post_id,))
    if not post:
        raise HTTPException(404, "Post not found")

    rows = await db.execute_fetchall(
        "SELECT * FROM reactions WHERE post_id = ? ORDER BY created_at", (post_id,)
    )
    return [dict(r) for r in rows]
