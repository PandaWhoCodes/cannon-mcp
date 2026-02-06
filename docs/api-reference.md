# API Reference

Base URL: `http://localhost:8000`

## Categories

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/categories` | List all categories with thread counts |
| POST | `/api/categories` | Create a category |
| GET | `/api/categories/{id}` | Get a single category |
| PUT | `/api/categories/{id}` | Update a category (name, description) |
| DELETE | `/api/categories/{id}` | Delete a category (cascades threads/posts) |

### Create/Update Body

```json
{ "name": "General", "description": "Talk about anything" }
```

---

## Threads

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/categories/{id}/threads` | List threads in a category (paginated) |
| POST | `/api/threads` | Create a thread (with first post and tags) |
| GET | `/api/threads/{id}` | Get thread detail with post count and tags |
| PUT | `/api/threads/{id}` | Update thread (title, is_pinned, is_locked) |
| DELETE | `/api/threads/{id}` | Delete thread (cascades posts, FTS entries) |

### Query Params (list)

- `page` (default 1)
- `page_size` (default 20, max 100)
- `sort`: `created_at` | `updated_at` | `post_count`
- `order`: `asc` | `desc`

### Create Body

```json
{
  "category_id": 1,
  "title": "Thread title",
  "author_name": "username",
  "content": "First post content",
  "tags": ["python", "api"]
}
```

---

## Posts

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/threads/{id}/posts` | List posts in a thread (paginated, includes reaction counts) |
| POST | `/api/posts` | Create a post (fails if thread is locked) |
| GET | `/api/posts/{id}` | Get a single post with reaction counts |
| PUT | `/api/posts/{id}` | Edit post content |
| DELETE | `/api/posts/{id}` | Delete a post |

### Create Body

```json
{ "thread_id": 1, "author_name": "username", "content": "Post content" }
```

### Post Response

Includes `upvotes` and `downvotes` counts.

---

## Reactions

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/posts/{id}/reactions` | List all reactions on a post |
| POST | `/api/posts/{id}/reactions` | Add a reaction |
| DELETE | `/api/posts/{id}/reactions/{type}?reactor_name=...` | Remove a reaction |

### Create Body

```json
{ "reaction_type": "upvote", "reactor_name": "username" }
```

Reaction types: `upvote`, `downvote`. Each user can only have one reaction of each type per post (unique constraint).

---

## Tags

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/tags` | List all tags with thread counts (sorted by popularity) |
| POST | `/api/threads/{id}/tags` | Add tags to a thread |
| DELETE | `/api/threads/{id}/tags/{tag_name}` | Remove a tag from a thread |
| GET | `/api/tags/{name}/threads` | Browse threads by tag (paginated) |

### Add Tags Body

```json
{ "tags": ["python", "tutorial"] }
```

---

## Search

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/search?q=...&type=...` | Full-text search |

### Query Params

- `q` (required): Search query string
- `type`: `threads` | `posts` | `all` (default: `threads`)

Returns results ranked by relevance score (FTS5 rank).

---

## Stats

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/stats` | Forum-wide aggregate counts |
| GET | `/api/stats/trending` | Top 10 trending threads |

### Stats Response

```json
{
  "total_categories": 5,
  "total_threads": 7,
  "total_posts": 14,
  "total_reactions": 9,
  "total_tags": 15
}
```

### Trending Score

`score = (post_count * 2) + reaction_count`

---

## Utility

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API info and endpoint listing |
| GET | `/api/health` | Health check (verifies DB connection) |
| GET | `/docs` | Interactive Swagger UI |
| GET | `/openapi.json` | OpenAPI 3.x spec |

---

## Pagination

All list endpoints return:

```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```
