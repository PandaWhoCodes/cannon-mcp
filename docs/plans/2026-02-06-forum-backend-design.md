# Forum Backend Design

## Tech Stack
- FastAPI (Python)
- SQLite via aiosqlite
- Pydantic models for request/response validation
- No authentication

## Data Model

### Categories
- id (INTEGER PK)
- name (TEXT UNIQUE NOT NULL)
- description (TEXT)
- created_at (TIMESTAMP)

### Threads
- id (INTEGER PK)
- category_id (FK -> categories)
- title (TEXT NOT NULL)
- author_name (TEXT NOT NULL)
- is_pinned (BOOLEAN DEFAULT FALSE)
- is_locked (BOOLEAN DEFAULT FALSE)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

### Posts
- id (INTEGER PK)
- thread_id (FK -> threads)
- author_name (TEXT NOT NULL)
- content (TEXT NOT NULL)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

### Reactions
- id (INTEGER PK)
- post_id (FK -> posts)
- reaction_type (TEXT CHECK IN ('upvote', 'downvote'))
- reactor_name (TEXT NOT NULL)
- created_at (TIMESTAMP)
- UNIQUE(post_id, reactor_name, reaction_type)

### Thread_Tags
- thread_id (FK -> threads)
- tag_name (TEXT NOT NULL)
- PRIMARY KEY (thread_id, tag_name)

### FTS Virtual Table
- threads_fts (title, content from first post)
- posts_fts (content)

## API Endpoints

### Categories
- GET    /api/categories
- POST   /api/categories
- GET    /api/categories/{id}
- PUT    /api/categories/{id}
- DELETE /api/categories/{id}

### Threads
- GET    /api/categories/{id}/threads  (paginated, sortable by created_at/updated_at/post_count)
- POST   /api/threads
- GET    /api/threads/{id}
- PUT    /api/threads/{id}
- DELETE /api/threads/{id}

### Posts
- GET    /api/threads/{id}/posts (paginated)
- POST   /api/posts
- GET    /api/posts/{id}
- PUT    /api/posts/{id}
- DELETE /api/posts/{id}

### Reactions
- POST   /api/posts/{id}/reactions
- DELETE /api/posts/{id}/reactions/{type}

### Tags
- GET    /api/tags
- POST   /api/threads/{id}/tags
- DELETE /api/threads/{id}/tags/{tag}
- GET    /api/tags/{name}/threads

### Search & Stats
- GET    /api/search?q=...&type=threads|posts
- GET    /api/stats
- GET    /api/stats/trending

## Project Structure
```
app/
  main.py          - FastAPI app, CORS, lifespan
  database.py      - SQLite connection, schema init
  models.py        - Pydantic models
  routers/
    categories.py
    threads.py
    posts.py
    reactions.py
    tags.py
    search.py
    stats.py
requirements.txt
```

## Implementation Steps
1. Switch to backend branch
2. Set up project structure and requirements.txt
3. Implement database.py (schema, connection management)
4. Implement models.py (all Pydantic schemas)
5. Implement category routes
6. Implement thread routes
7. Implement post routes
8. Implement reaction routes
9. Implement tag routes
10. Implement search (FTS) routes
11. Implement stats routes
12. Add CORS middleware, seed data, test the server
