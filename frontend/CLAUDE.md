# Forum Frontend

## Overview

React 19 + TypeScript forum client that consumes the backend API. Built with Vite, styled with Tailwind CSS v4, data fetching via TanStack React Query.

## Documentation

Detailed docs live in two locations — check both:
- `/CLAUDE.md` (this file) — top-level project context
- `/docs/` — detailed component reference, API integration, and architecture docs

## Tech Stack

- **Framework:** React 19 + TypeScript 5.9
- **Build:** Vite 7
- **Styling:** Tailwind CSS v4 (utility classes only, no custom CSS)
- **Data Fetching:** TanStack React Query v5 (30s stale time, 1 retry)
- **Routing:** React Router v7
- **Auth:** None — uses "anonymous" as default user for votes

## Project Structure

```
forum-frontend/
  src/
    api/
      client.ts            # HTTP client with all API endpoint functions
      types.ts             # TypeScript interfaces for API models
    components/
      Layout.tsx           # Main layout: header, search bar, nav
      PostCard.tsx          # Single post display with author/timestamp
      ThreadRow.tsx         # Thread list item (count, title, tags)
      VoteButtons.tsx       # Upvote/downvote with score display
      TagBadge.tsx          # Clickable tag pill, links to tag page
      Pagination.tsx        # Prev/Next page controls
    pages/
      HomePage.tsx          # Stats, categories list, trending sidebar
      CategoryPage.tsx      # Threads in category (sortable)
      ThreadPage.tsx        # Full thread with posts and reply form
      NewThreadPage.tsx     # Create thread form (title, content, tags)
      SearchPage.tsx        # Full-text search with type filter
      TagsPage.tsx          # All tags with thread counts
      TagThreadsPage.tsx    # Threads filtered by tag
    App.tsx                 # Router configuration
    main.tsx                # Entry point, QueryClient setup
    index.css               # Tailwind CSS import
    utils.ts                # timeAgo() helper
  vite.config.ts            # Dev proxy (/api -> localhost:8000)
  package.json
```

## Running

```bash
cd forum-frontend
npm install
npm run dev
```

Requires the backend running on `http://localhost:8000`. Vite proxies `/api` requests to the backend.

## Key Patterns

- **API Client:** All backend calls go through `src/api/client.ts`. Generic `request<T>()` wraps fetch with error handling.
- **React Query:** Every page uses `useQuery`/`useMutation`. Cache is invalidated after mutations to refetch fresh data.
- **Pagination:** Server-side. Components receive `{items, total, page, page_size, total_pages}` and render `Pagination` controls.
- **Routing:** Nested — Home -> Category -> Thread -> Posts. Tag pages are separate routes.
- **Voting:** Uses hardcoded "anonymous" user. Upvote/downvote via React Query mutations.

## Common Tasks

- **Add a new page:** Create in `src/pages/`, add route in `App.tsx`.
- **Add a component:** Create in `src/components/`, import where needed.
- **Add an API call:** Add function in `src/api/client.ts`, add types in `src/api/types.ts`.
- **Change styling:** All Tailwind utility classes — edit directly in component JSX.
