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

### Create Body

```json
{ "name": "General", "description": "Talk about anything" }
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| name | string | Yes | min 1 char, max 100 chars, must be unique |
| description | string | No | Defaults to `""` |

### Update Body

```json
{ "name": "Updated Name", "description": "Updated description" }
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| name | string | No | min 1 char, max 100 chars, must be unique |
| description | string | No | |

### Category Response

All category endpoints return:

```json
{
  "id": 1,
  "name": "General",
  "description": "Talk about anything",
  "created_at": "2026-02-06 12:00:00",
  "thread_count": 3
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| name | string | Category name |
| description | string | Category description |
| created_at | string | ISO timestamp of creation |
| thread_count | integer | Number of threads in this category |

`GET /api/categories` returns `Category[]` (not paginated).

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

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| category_id | integer | Yes | Must reference an existing category |
| title | string | Yes | min 1 char, max 300 chars |
| author_name | string | **Yes** | **min 1 char**, max 50 chars |
| content | string | Yes | min 1 char (becomes the first post) |
| tags | string[] | No | Defaults to `[]`, tags are lowercased and trimmed |

### Update Body

```json
{ "title": "New title", "is_pinned": true, "is_locked": false }
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| title | string | No | min 1 char, max 300 chars |
| is_pinned | boolean | No | |
| is_locked | boolean | No | |

### ThreadSummary Response

Returned by `GET /api/categories/{id}/threads` (as paginated `items`) and `GET /api/tags/{name}/threads`:

```json
{
  "id": 1,
  "category_id": 1,
  "title": "Thread title",
  "author_name": "username",
  "is_pinned": false,
  "is_locked": false,
  "created_at": "2026-02-06 12:00:00",
  "updated_at": "2026-02-06 12:00:00",
  "post_count": 5,
  "tags": ["python", "api"]
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| category_id | integer | Parent category ID |
| title | string | Thread title |
| author_name | string | Thread author |
| is_pinned | boolean | Whether the thread is pinned (pinned threads sort first) |
| is_locked | boolean | Whether the thread is locked (no new posts allowed) |
| created_at | string | ISO timestamp of creation |
| updated_at | string | ISO timestamp of last update |
| post_count | integer | Number of posts in the thread |
| tags | string[] | List of tag names |

### ThreadDetail Response

Returned by `GET /api/threads/{id}`, `POST /api/threads`, and `PUT /api/threads/{id}`. Extends ThreadSummary with `category_name`:

```json
{
  "id": 1,
  "category_id": 1,
  "title": "Thread title",
  "author_name": "username",
  "is_pinned": false,
  "is_locked": false,
  "created_at": "2026-02-06 12:00:00",
  "updated_at": "2026-02-06 12:00:00",
  "post_count": 5,
  "tags": ["python", "api"],
  "category_name": "General"
}
```

| Field | Type | Description |
|-------|------|-------------|
| *(all ThreadSummary fields)* | | |
| category_name | string | Name of the parent category |

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

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| thread_id | integer | Yes | Must reference an existing, unlocked thread |
| author_name | string | **Yes** | **min 1 char**, max 50 chars |
| content | string | Yes | min 1 char |

Returns **403** if the thread is locked.

### Update Body

```json
{ "content": "Updated post content" }
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| content | string | Yes | min 1 char |

### Post Response

Returned by `GET /api/posts/{id}`, `POST /api/posts`, and `PUT /api/posts/{id}`:

```json
{
  "id": 1,
  "thread_id": 1,
  "author_name": "username",
  "content": "Post content",
  "created_at": "2026-02-06 12:00:00",
  "updated_at": "2026-02-06 12:00:00",
  "upvotes": 3,
  "downvotes": 1
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| thread_id | integer | Parent thread ID |
| author_name | string | Post author |
| content | string | Post content |
| created_at | string | ISO timestamp of creation |
| updated_at | string | ISO timestamp of last edit |
| upvotes | integer | Count of upvote reactions |
| downvotes | integer | Count of downvote reactions |

### Posts List Response

`GET /api/threads/{id}/posts` returns the standard paginated response **plus** an extra `is_locked` field:

```json
{
  "items": [ /* Post objects */ ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3,
  "is_locked": false
}
```

| Field | Type | Description |
|-------|------|-------------|
| *(all standard pagination fields)* | | See [Pagination](#pagination) |
| is_locked | boolean | Whether the parent thread is locked |

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

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| reaction_type | string | Yes | Must be `"upvote"` or `"downvote"` |
| reactor_name | string | Yes | min 1 char, max 50 chars |

Each user can only have one reaction of each type per post (unique constraint). Returns **409** if the reaction already exists.

### Reaction Response

Returned by `POST /api/posts/{id}/reactions`:

```json
{
  "id": 1,
  "post_id": 1,
  "reaction_type": "upvote",
  "reactor_name": "username",
  "created_at": "2026-02-06 12:00:00"
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| post_id | integer | Parent post ID |
| reaction_type | string | `"upvote"` or `"downvote"` |
| reactor_name | string | User who reacted |
| created_at | string | ISO timestamp of creation |

`GET /api/posts/{id}/reactions` returns `Reaction[]` (not paginated).

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

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| tags | string[] | Yes | At least 1 tag, tags are lowercased and trimmed |

### Add Tags Response

```json
{
  "thread_id": 1,
  "tags": ["api", "python", "tutorial"]
}
```

Returns the full list of tags on the thread after adding.

### Tag Response

Returned by `GET /api/tags`:

```json
{ "name": "python", "thread_count": 5 }
```

| Field | Type | Description |
|-------|------|-------------|
| name | string | Tag name |
| thread_count | integer | Number of threads with this tag |

`GET /api/tags` returns `Tag[]` (not paginated), sorted by thread_count descending.

`GET /api/tags/{name}/threads` returns a standard paginated response with `ThreadSummary` items (see [ThreadSummary Response](#threadsummary-response)).

---

## Search

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/search?q=...&type=...` | Full-text search |

### Query Params

- `q` (required): Search query string (min 1 char, max 200 chars)
- `type`: `threads` | `posts` | `all` (default: `threads`)

### Search Response

```json
{
  "query": "python",
  "type": "threads",
  "total": 2,
  "results": [
    {
      "type": "thread",
      "id": 1,
      "title": "Getting Started with Python",
      "content": "First post content (truncated to 300 chars)...",
      "author_name": "username",
      "thread_id": null,
      "relevance_score": 1.5
    },
    {
      "type": "post",
      "id": 5,
      "title": null,
      "content": "Post content (truncated to 300 chars)...",
      "author_name": "username",
      "thread_id": 3,
      "relevance_score": 1.2
    }
  ]
}
```

#### SearchResponse

| Field | Type | Description |
|-------|------|-------------|
| query | string | The original search query |
| type | string | The search type used |
| total | integer | Number of results |
| results | SearchResult[] | Results sorted by relevance (highest first) |

#### SearchResult

| Field | Type | Description |
|-------|------|-------------|
| type | string | `"thread"` or `"post"` |
| id | integer | Thread ID or Post ID depending on type |
| title | string or null | Thread title (present for threads, `null` for posts) |
| content | string | Content preview, truncated to 300 characters |
| author_name | string | Author of the thread or post |
| thread_id | integer or null | Parent thread ID (present for posts, `null` for threads) |
| relevance_score | float | FTS5 relevance score (higher = more relevant) |

Search is **not paginated** — returns up to 50 results per type (max 100 for `type=all`).

---

## Stats

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/stats` | Forum-wide aggregate counts |
| GET | `/api/stats/trending` | Top 10 trending threads |

### ForumStats Response

```json
{
  "total_categories": 5,
  "total_threads": 7,
  "total_posts": 14,
  "total_reactions": 9,
  "total_tags": 15
}
```

| Field | Type | Description |
|-------|------|-------------|
| total_categories | integer | Total number of categories |
| total_threads | integer | Total number of threads |
| total_posts | integer | Total number of posts |
| total_reactions | integer | Total number of reactions |
| total_tags | integer | Total number of unique tags |

### TrendingThread Response

`GET /api/stats/trending` returns `TrendingThread[]` (not paginated, max 10):

```json
{
  "id": 1,
  "title": "Hot Topic",
  "author_name": "username",
  "category_name": "General",
  "post_count": 10,
  "reaction_count": 5,
  "score": 25.0,
  "created_at": "2026-02-06 12:00:00"
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Thread ID |
| title | string | Thread title |
| author_name | string | Thread author |
| category_name | string | Parent category name |
| post_count | integer | Number of posts in the thread |
| reaction_count | integer | Number of reactions across all posts |
| score | float | Trending score: `(post_count * 2) + reaction_count` |
| created_at | string | ISO timestamp of creation |

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

| Field | Type | Description |
|-------|------|-------------|
| items | array | Array of resource objects for the current page |
| total | integer | Total number of items across all pages |
| page | integer | Current page number (1-based) |
| page_size | integer | Number of items per page |
| total_pages | integer | Total number of pages |

**Exception:** `GET /api/threads/{id}/posts` also includes `is_locked` (boolean) in the paginated response. See [Posts List Response](#posts-list-response).

---

## Error Responses

| Status | Meaning | When |
|--------|---------|------|
| 400 | Bad Request | Constraint violations (e.g. duplicate category name) |
| 403 | Forbidden | Posting to a locked thread |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Duplicate reaction (same user, same type, same post) |
| 422 | Validation Error | Request body fails Pydantic validation (missing required fields, min/max length) |
