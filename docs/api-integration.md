# API Integration

## Client Setup

All API calls go through `src/api/client.ts`. The generic `request<T>()` function:

1. Prepends `/api` base URL
2. Sets `Content-Type: application/json`
3. Stringifies request bodies
4. Throws on non-OK responses

## TypeScript Types

All API response shapes are defined in `src/api/types.ts`:

- `Category` — id, name, description, thread_count
- `ThreadSummary` — id, title, author_name, is_pinned, is_locked, post_count, tags
- `ThreadDetail` — extends ThreadSummary with category_name
- `Post` — id, thread_id, author_name, content, upvotes, downvotes
- `Reaction` — id, post_id, reaction_type, reactor_name
- `Tag` — name, thread_count
- `SearchResult` — type, id, title, content, author_name, thread_id, relevance_score
- `SearchResponse` — query, type, total, results (wraps SearchResult[])
- `ForumStats` — total counts for categories, threads, posts, reactions, tags
- `TrendingThread` — id, title, author_name, category_name, post_count, reaction_count, score
- `PaginatedResponse<T>` — items, total, page, page_size, total_pages

## API Functions

### Categories
- `getCategories()` → `Category[]`
- `getCategory(id)` → `Category`
- `createCategory(data)` → `Category`

### Threads
- `getThreads(categoryId, params?)` → `PaginatedResponse<ThreadSummary>`
- `getThread(id)` → `ThreadDetail`
- `createThread(data)` → `ThreadDetail`
- `updateThread(id, data)` → `ThreadDetail`
- `deleteThread(id)` → `void`

### Posts
- `getPosts(threadId, params?)` → `PaginatedResponse<Post>`
- `createPost(data)` → `Post`
- `deletePost(id)` → `void`

### Reactions
- `addReaction(postId, data)` → `Reaction`
- `removeReaction(postId, type, reactorName)` → `void`

### Tags & Search
- `getTags()` → `Tag[]`
- `getThreadsByTag(tagName, params?)` → `PaginatedResponse<ThreadSummary>`
- `search(query, type)` → `SearchResponse`

### Stats
- `getStats()` → `ForumStats`
- `getTrending()` → `TrendingThread[]`

## React Query Usage

Every page uses React Query hooks:

```typescript
// Fetching
const { data, isLoading } = useQuery({
  queryKey: ["categories"],
  queryFn: getCategories,
});

// Mutating
const mutation = useMutation({
  mutationFn: (data) => createPost(data),
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ["posts", threadId] }),
});
```

Query keys follow the pattern: `[resource, ...identifiers, ...params]`

## Dev Proxy

Vite config proxies `/api` to the backend:

```typescript
// vite.config.ts
server: {
  proxy: {
    "/api": { target: "http://localhost:8000" }
  }
}
```

In production, configure a reverse proxy (nginx, Caddy) to route `/api` to the backend.
