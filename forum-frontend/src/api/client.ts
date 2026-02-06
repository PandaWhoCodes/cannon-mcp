import type {
  Category,
  ThreadSummary,
  ThreadDetail,
  Post,
  Reaction,
  Tag,
  PaginatedResponse,
  ForumStats,
  TrendingThread,
  SearchResponse,
} from './types'

const BASE = '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed: ${res.status}`)
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

// Categories
export const getCategories = () => request<Category[]>('/categories')

export const getCategory = (id: number) => request<Category>(`/categories/${id}`)

export const createCategory = (data: { name: string; description: string }) =>
  request<Category>('/categories', { method: 'POST', body: JSON.stringify(data) })

// Threads
export const getThreads = (
  categoryId: number,
  params?: { page?: number; page_size?: number; sort?: string; order?: string }
) => {
  const sp = new URLSearchParams()
  if (params?.page) sp.set('page', String(params.page))
  if (params?.page_size) sp.set('page_size', String(params.page_size))
  if (params?.sort) sp.set('sort', params.sort)
  if (params?.order) sp.set('order', params.order)
  const qs = sp.toString()
  return request<PaginatedResponse<ThreadSummary>>(`/categories/${categoryId}/threads${qs ? `?${qs}` : ''}`)
}

export const getThread = (id: number) => request<ThreadDetail>(`/threads/${id}`)

export const createThread = (data: {
  category_id: number
  title: string
  author_name: string
  content: string
  tags?: string[]
}) => request<ThreadDetail>('/threads', { method: 'POST', body: JSON.stringify(data) })

export const updateThread = (id: number, data: { title?: string; is_pinned?: boolean; is_locked?: boolean }) =>
  request<ThreadDetail>(`/threads/${id}`, { method: 'PUT', body: JSON.stringify(data) })

export const deleteThread = (id: number) =>
  request<void>(`/threads/${id}`, { method: 'DELETE' })

// Posts
export const getPosts = (threadId: number, params?: { page?: number; page_size?: number }) => {
  const sp = new URLSearchParams()
  if (params?.page) sp.set('page', String(params.page))
  if (params?.page_size) sp.set('page_size', String(params.page_size))
  const qs = sp.toString()
  return request<PaginatedResponse<Post>>(`/threads/${threadId}/posts${qs ? `?${qs}` : ''}`)
}

export const createPost = (data: { thread_id: number; author_name: string; content: string }) =>
  request<Post>('/posts', { method: 'POST', body: JSON.stringify(data) })

export const deletePost = (id: number) =>
  request<void>(`/posts/${id}`, { method: 'DELETE' })

// Reactions
export const addReaction = (postId: number, data: { reaction_type: 'upvote' | 'downvote'; reactor_name: string }) =>
  request<Reaction>(`/posts/${postId}/reactions`, { method: 'POST', body: JSON.stringify(data) })

export const removeReaction = (postId: number, type: string, reactorName: string) =>
  request<void>(`/posts/${postId}/reactions/${type}?reactor_name=${encodeURIComponent(reactorName)}`, {
    method: 'DELETE',
  })

// Tags
export const getTags = () => request<Tag[]>('/tags')

export const getThreadsByTag = (tagName: string, params?: { page?: number }) => {
  const sp = new URLSearchParams()
  if (params?.page) sp.set('page', String(params.page))
  const qs = sp.toString()
  return request<PaginatedResponse<ThreadSummary>>(`/tags/${encodeURIComponent(tagName)}/threads${qs ? `?${qs}` : ''}`)
}

// Search
export const search = (q: string, type: 'threads' | 'posts' | 'all' = 'threads') => {
  const sp = new URLSearchParams({ q, type })
  return request<SearchResponse>(`/search?${sp}`)
}

// Stats
export const getStats = () => request<ForumStats>('/stats')
export const getTrending = () => request<TrendingThread[]>('/stats/trending')
