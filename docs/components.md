# Component Reference

## Layout Components

### Layout (`src/components/Layout.tsx`)

Top-level wrapper for all pages. Renders:
- Header with forum title
- Search bar (navigates to `/search?q=...`)
- Nav links: Home, Tags
- `<Outlet />` for child routes

## Reusable Components

### ThreadRow (`src/components/ThreadRow.tsx`)

Displays a single thread in a list. Shows:
- Post count badge
- Thread title (linked to thread page)
- Author name, creation date (via `timeAgo()`)
- Tag badges
- Pinned/locked indicators

### PostCard (`src/components/PostCard.tsx`)

Displays a single post within a thread. Shows:
- Author name
- Timestamp
- Post content
- Vote buttons (via `VoteButtons`)

### VoteButtons (`src/components/VoteButtons.tsx`)

Upvote/downvote controls for a post.
- Displays current score (upvotes - downvotes)
- Sends mutations to `POST /api/posts/{id}/reactions`
- Uses "anonymous" as reactor name
- Invalidates query cache on vote

### TagBadge (`src/components/TagBadge.tsx`)

Small clickable pill displaying a tag name. Links to `/tags/{name}` to show all threads with that tag.

### Pagination (`src/components/Pagination.tsx`)

Prev/Next navigation for paginated lists. Receives `page`, `totalPages`, and `onPageChange` callback. Disables buttons at boundaries.

## Pages

### HomePage (`src/pages/HomePage.tsx`)

- Fetches `/api/stats` for forum-wide counts
- Fetches `/api/categories` for category list
- Fetches `/api/stats/trending` for trending threads sidebar
- Grid layout: categories on left, trending on right

### CategoryPage (`src/pages/CategoryPage.tsx`)

- Fetches category details and threads via `/api/categories/{id}/threads`
- Sort dropdown: by activity, creation date, post count
- Paginated thread list using `ThreadRow`

### ThreadPage (`src/pages/ThreadPage.tsx`)

- Fetches thread details and paginated posts
- Renders each post via `PostCard`
- Reply form at bottom (disabled if thread is locked)
- Shows thread tags

### NewThreadPage (`src/pages/NewThreadPage.tsx`)

- Form: title, author name, content, tags (comma-separated)
- Posts to `/api/threads` with category_id from route param (`/categories/:id/new`)
- Redirects to new thread page on success

### SearchPage (`src/pages/SearchPage.tsx`)

- Search input + type filter (threads, posts, all)
- Fetches `/api/search?q=...&type=...`
- Displays results with relevance score

### TagsPage (`src/pages/TagsPage.tsx`)

- Fetches `/api/tags` — all tags with thread counts
- Grid of tag badges with counts

### TagThreadsPage (`src/pages/TagThreadsPage.tsx`)

- Fetches `/api/tags/{name}/threads`
- Paginated thread list filtered by tag
