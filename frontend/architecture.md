# Frontend Architecture

## Overview

Single-page React application that communicates with the forum backend API. No server-side rendering — fully client-side with Vite dev server proxying API requests.

## Data Flow

```
User interaction
  │
  ▼
React Component (page or component)
  │
  ▼
React Query (useQuery / useMutation)
  │
  ▼
API Client (src/api/client.ts)
  │
  ▼
Vite Proxy (/api -> localhost:8000)
  │
  ▼
Backend FastAPI Server
```

## Routing

```
/                          → HomePage (stats, categories, trending)
/category/:id              → CategoryPage (threads list, sortable)
/thread/:id                → ThreadPage (posts, reply form)
/new-thread?category=:id   → NewThreadPage (create form)
/search?q=...&type=...     → SearchPage (full-text search)
/tags                      → TagsPage (all tags)
/tags/:name                → TagThreadsPage (threads by tag)
```

All routes are wrapped in `Layout` which provides the header, search bar, and navigation.

## State Management

No global state store. All server state is managed by React Query:

- **Queries** fetch data with automatic caching (30s stale time)
- **Mutations** create/update/delete data, then invalidate relevant query caches
- **No optimistic updates** — waits for server confirmation before updating UI

## Key Design Decisions

### Vite Proxy

Development server proxies `/api` to `http://localhost:8000`. This avoids CORS issues during development and means the API client uses relative URLs (`/api/categories` not `http://localhost:8000/api/categories`).

### No Auth

Votes use a hardcoded "anonymous" username. Post/thread creation has an optional author name field that defaults to empty. This matches the backend's no-auth design.

### Tailwind Only

No CSS modules, styled-components, or custom CSS files. Everything is Tailwind utility classes in JSX. This keeps styling co-located with components and avoids style conflicts.

### Server-Side Pagination

All list views (threads, posts, tag results) use server-side pagination. The backend returns page metadata and the frontend renders Prev/Next controls.
