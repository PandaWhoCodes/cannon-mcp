from fastapi import APIRouter, HTTPException
from app.database import get_db
from app.models import Category, CategoryCreate, CategoryUpdate

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[Category])
async def list_categories():
    db = await get_db()
    rows = await db.execute_fetchall("""
        SELECT c.*, COALESCE(t.cnt, 0) AS thread_count
        FROM categories c
        LEFT JOIN (SELECT category_id, COUNT(*) AS cnt FROM threads GROUP BY category_id) t
            ON t.category_id = c.id
        ORDER BY c.name
    """)
    return [dict(r) for r in rows]


@router.post("", response_model=Category, status_code=201)
async def create_category(body: CategoryCreate):
    db = await get_db()
    try:
        cursor = await db.execute(
            "INSERT INTO categories (name, description) VALUES (?, ?)",
            (body.name, body.description),
        )
        await db.commit()
    except Exception:
        raise HTTPException(400, "Category name already exists")
    row = await db.execute_fetchall(
        "SELECT *, 0 AS thread_count FROM categories WHERE id = ?", (cursor.lastrowid,)
    )
    return dict(row[0])


@router.get("/{category_id}", response_model=Category)
async def get_category(category_id: int):
    db = await get_db()
    rows = await db.execute_fetchall("""
        SELECT c.*, COALESCE(t.cnt, 0) AS thread_count
        FROM categories c
        LEFT JOIN (SELECT category_id, COUNT(*) AS cnt FROM threads GROUP BY category_id) t
            ON t.category_id = c.id
        WHERE c.id = ?
    """, (category_id,))
    if not rows:
        raise HTTPException(404, "Category not found")
    return dict(rows[0])


@router.put("/{category_id}", response_model=Category)
async def update_category(category_id: int, body: CategoryUpdate):
    db = await get_db()
    existing = await db.execute_fetchall("SELECT * FROM categories WHERE id = ?", (category_id,))
    if not existing:
        raise HTTPException(404, "Category not found")

    updates = {}
    if body.name is not None:
        updates["name"] = body.name
    if body.description is not None:
        updates["description"] = body.description

    if updates:
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [category_id]
        try:
            await db.execute(f"UPDATE categories SET {set_clause} WHERE id = ?", values)
            await db.commit()
        except Exception:
            raise HTTPException(400, "Category name already exists")

    rows = await db.execute_fetchall("""
        SELECT c.*, COALESCE(t.cnt, 0) AS thread_count
        FROM categories c
        LEFT JOIN (SELECT category_id, COUNT(*) AS cnt FROM threads GROUP BY category_id) t
            ON t.category_id = c.id
        WHERE c.id = ?
    """, (category_id,))
    return dict(rows[0])


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: int):
    db = await get_db()
    existing = await db.execute_fetchall("SELECT * FROM categories WHERE id = ?", (category_id,))
    if not existing:
        raise HTTPException(404, "Category not found")
    await db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    await db.commit()
