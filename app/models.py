from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


# --- Categories ---

class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = ""


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None


class Category(BaseModel):
    id: int
    name: str
    description: str
    created_at: str
    thread_count: int = 0


# --- Threads ---

class ThreadCreate(BaseModel):
    category_id: int
    title: str = Field(min_length=1, max_length=300)
    author_name: str = Field(min_length=1, max_length=50)
    content: str = Field(min_length=1, description="Content of the first post")
    tags: list[str] = []


class ThreadUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    is_pinned: bool | None = None
    is_locked: bool | None = None


class ThreadSummary(BaseModel):
    id: int
    category_id: int
    title: str
    author_name: str
    is_pinned: bool
    is_locked: bool
    created_at: str
    updated_at: str
    post_count: int = 0
    tags: list[str] = []


class ThreadDetail(ThreadSummary):
    category_name: str = ""


# --- Posts ---

class PostCreate(BaseModel):
    thread_id: int
    author_name: str = Field(min_length=1, max_length=50)
    content: str = Field(min_length=1)


class PostUpdate(BaseModel):
    content: str = Field(min_length=1)


class Post(BaseModel):
    id: int
    thread_id: int
    author_name: str
    content: str
    created_at: str
    updated_at: str
    upvotes: int = 0
    downvotes: int = 0


# --- Reactions ---

class ReactionCreate(BaseModel):
    reaction_type: Literal["upvote", "downvote"]
    reactor_name: str = Field(min_length=1, max_length=50)


class Reaction(BaseModel):
    id: int
    post_id: int
    reaction_type: str
    reactor_name: str
    created_at: str


# --- Tags ---

class TagsAdd(BaseModel):
    tags: list[str] = Field(min_length=1)


class Tag(BaseModel):
    name: str
    thread_count: int = 0


# --- Search ---

class SearchResult(BaseModel):
    type: str  # "thread" or "post"
    id: int
    title: str | None = None
    content: str
    author_name: str
    thread_id: int | None = None
    relevance_score: float = 0.0


class SearchResponse(BaseModel):
    query: str
    type: str
    total: int
    results: list[SearchResult]


# --- Stats ---

class ForumStats(BaseModel):
    total_categories: int
    total_threads: int
    total_posts: int
    total_reactions: int
    total_tags: int


class TrendingThread(BaseModel):
    id: int
    title: str
    author_name: str
    category_name: str
    post_count: int
    reaction_count: int
    score: float
    created_at: str


# --- Pagination ---

class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
