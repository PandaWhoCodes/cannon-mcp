export interface Category {
  id: number
  name: string
  description: string
  created_at: string
  thread_count: number
}

export interface ThreadSummary {
  id: number
  category_id: number
  title: string
  author_name: string
  is_pinned: boolean
  is_locked: boolean
  created_at: string
  updated_at: string
  post_count: number
  tags: string[]
}

export interface ThreadDetail extends ThreadSummary {
  category_name: string
}

export interface Post {
  id: number
  thread_id: number
  author_name: string
  content: string
  created_at: string
  updated_at: string
  upvotes: number
  downvotes: number
}

export interface Reaction {
  id: number
  post_id: number
  reaction_type: 'upvote' | 'downvote'
  reactor_name: string
  created_at: string
}

export interface Tag {
  name: string
  thread_count: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ForumStats {
  total_categories: number
  total_threads: number
  total_posts: number
  total_reactions: number
  total_tags: number
}

export interface TrendingThread {
  id: number
  title: string
  author_name: string
  category_id: number
  category_name: string
  post_count: number
  reaction_count: number
  score: number
  created_at: string
}

export interface SearchResult {
  type: 'thread' | 'post'
  id: number
  title: string | null
  content: string
  author_name: string
  thread_id: number | null
  relevance_score: number
}

export interface SearchResponse {
  query: string
  type: string
  total: number
  results: SearchResult[]
}
