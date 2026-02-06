from fastapi import APIRouter, Query
from app.database import get_db
from app.models import SearchResponse, SearchResult

router = APIRouter(tags=["search"])


@router.get("/api/search", response_model=SearchResponse)
async def search(
    q: str = Query(min_length=1, max_length=200),
    type: str = Query("threads", pattern="^(threads|posts|all)$"),
):
    db = await get_db()
    results: list[SearchResult] = []

    if type in ("threads", "all"):
        rows = await db.execute_fetchall("""
            SELECT fts.thread_id AS id, fts.title, fts.content, t.author_name,
                   rank AS relevance_score
            FROM threads_fts fts
            JOIN threads t ON t.id = fts.thread_id
            WHERE threads_fts MATCH ?
            ORDER BY rank
            LIMIT 50
        """, (q,))
        for r in rows:
            results.append(SearchResult(
                type="thread",
                id=r["id"],
                title=r["title"],
                content=r["content"][:300],
                author_name=r["author_name"],
                relevance_score=abs(r["relevance_score"]),
            ))

    if type in ("posts", "all"):
        rows = await db.execute_fetchall("""
            SELECT fts.post_id AS id, fts.content, p.author_name, p.thread_id,
                   rank AS relevance_score
            FROM posts_fts fts
            JOIN posts p ON p.id = fts.post_id
            WHERE posts_fts MATCH ?
            ORDER BY rank
            LIMIT 50
        """, (q,))
        for r in rows:
            results.append(SearchResult(
                type="post",
                id=r["id"],
                content=r["content"][:300],
                author_name=r["author_name"],
                thread_id=r["thread_id"],
                relevance_score=abs(r["relevance_score"]),
            ))

    # Sort by relevance
    results.sort(key=lambda x: x.relevance_score, reverse=True)

    return SearchResponse(
        query=q,
        type=type,
        total=len(results),
        results=results,
    )
