from fastapi import APIRouter
from app.database import get_db
from app.models import ForumStats, TrendingThread

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=ForumStats)
async def get_stats():
    db = await get_db()

    cats = await db.execute_fetchall("SELECT COUNT(*) AS c FROM categories")
    threads = await db.execute_fetchall("SELECT COUNT(*) AS c FROM threads")
    posts = await db.execute_fetchall("SELECT COUNT(*) AS c FROM posts")
    reactions = await db.execute_fetchall("SELECT COUNT(*) AS c FROM reactions")
    tags = await db.execute_fetchall("SELECT COUNT(DISTINCT tag_name) AS c FROM thread_tags")

    return ForumStats(
        total_categories=cats[0]["c"],
        total_threads=threads[0]["c"],
        total_posts=posts[0]["c"],
        total_reactions=reactions[0]["c"],
        total_tags=tags[0]["c"],
    )


@router.get("/trending", response_model=list[TrendingThread])
async def get_trending():
    db = await get_db()

    rows = await db.execute_fetchall("""
        SELECT
            t.id, t.title, t.author_name, t.created_at,
            c.name AS category_name,
            COALESCE(p.cnt, 0) AS post_count,
            COALESCE(r.cnt, 0) AS reaction_count,
            (COALESCE(p.cnt, 0) * 2 + COALESCE(r.cnt, 0)) AS score
        FROM threads t
        JOIN categories c ON c.id = t.category_id
        LEFT JOIN (SELECT thread_id, COUNT(*) AS cnt FROM posts GROUP BY thread_id) p
            ON p.thread_id = t.id
        LEFT JOIN (
            SELECT po.thread_id, COUNT(*) AS cnt
            FROM reactions re
            JOIN posts po ON po.id = re.post_id
            GROUP BY po.thread_id
        ) r ON r.thread_id = t.id
        ORDER BY score DESC, t.created_at DESC
        LIMIT 10
    """)

    return [dict(r) for r in rows]
