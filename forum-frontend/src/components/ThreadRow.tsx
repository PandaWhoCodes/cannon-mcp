import { Link } from 'react-router-dom'
import type { ThreadSummary } from '../api/types'
import TagBadge from './TagBadge'
import { timeAgo } from '../utils'

export default function ThreadRow({ thread }: { thread: ThreadSummary }) {
  return (
    <div className="flex items-start gap-3 p-3 bg-white border-b border-gray-100 hover:bg-gray-50">
      <div className="flex flex-col items-center min-w-[3rem] text-center">
        <span className="text-sm font-medium text-gray-700">{thread.post_count ?? 0}</span>
        <span className="text-[10px] text-gray-400">posts</span>
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          {thread.is_pinned ? (
            <span className="text-xs text-green-600 font-medium">PINNED</span>
          ) : null}
          {thread.is_locked ? (
            <span className="text-xs text-red-500 font-medium">LOCKED</span>
          ) : null}
          <Link
            to={`/threads/${thread.id}`}
            className="text-sm font-medium text-blue-600 hover:text-blue-800 truncate"
          >
            {thread.title}
          </Link>
        </div>
        <div className="flex items-center gap-2 mt-1">
          <span className="text-xs text-gray-500">
            by <span className="font-medium text-gray-600">{thread.author_name}</span>
          </span>
          <span className="text-xs text-gray-400">{timeAgo(thread.created_at)}</span>
          {thread.tags?.map(tag => (
            <TagBadge key={tag} name={tag} />
          ))}
        </div>
      </div>
    </div>
  )
}
