# Data Model

## ER Diagram (text)

```
categories 1──* threads 1──* posts 1──* reactions
                  │
                  *──* thread_tags
```

## Tables

### categories

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| name | TEXT | UNIQUE NOT NULL |
| description | TEXT | DEFAULT '' |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

### threads

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| category_id | INTEGER | FK -> categories(id) ON DELETE CASCADE |
| title | TEXT | NOT NULL |
| author_name | TEXT | NOT NULL |
| is_pinned | INTEGER | DEFAULT 0 |
| is_locked | INTEGER | DEFAULT 0 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

### posts

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| thread_id | INTEGER | FK -> threads(id) ON DELETE CASCADE |
| author_name | TEXT | NOT NULL |
| content | TEXT | NOT NULL |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

### reactions

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| post_id | INTEGER | FK -> posts(id) ON DELETE CASCADE |
| reaction_type | TEXT | CHECK IN ('upvote', 'downvote') |
| reactor_name | TEXT | NOT NULL |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| | | UNIQUE(post_id, reactor_name, reaction_type) |

### thread_tags

| Column | Type | Constraints |
|--------|------|-------------|
| thread_id | INTEGER | FK -> threads(id) ON DELETE CASCADE |
| tag_name | TEXT | NOT NULL |
| | | PRIMARY KEY (thread_id, tag_name) |

## FTS Virtual Tables

### threads_fts (FTS5)

| Column | Notes |
|--------|-------|
| title | Indexed, searchable |
| content | Indexed, first post content |
| thread_id | UNINDEXED, for joining back |

### posts_fts (FTS5)

| Column | Notes |
|--------|-------|
| content | Indexed, searchable |
| post_id | UNINDEXED, for joining back |

## Indexes

- `idx_threads_category` on threads(category_id)
- `idx_posts_thread` on posts(thread_id)
- `idx_reactions_post` on reactions(post_id)
- `idx_thread_tags_tag` on thread_tags(tag_name)

## Cascade Behavior

- Deleting a **category** cascades to its threads, which cascades to posts, reactions, tags, and FTS entries.
- Deleting a **thread** cascades to its posts, reactions, and FTS entries.
- Deleting a **post** cascades to its reactions and FTS entry.

## FTS Sync

FTS tables are **not** auto-synced. The application code must manually insert/update/delete FTS entries when modifying threads or posts. This is handled in the router code.
