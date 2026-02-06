import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { getTags } from '../api/client'

export default function TagsPage() {
  const tags = useQuery({ queryKey: ['tags'], queryFn: getTags })

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-900 mb-4">Tags</h1>

      {tags.isLoading && <p className="text-sm text-gray-500">Loading tags...</p>}
      {tags.error && <p className="text-sm text-red-500">Failed to load tags</p>}

      <div className="flex flex-wrap gap-2">
        {tags.data?.map(tag => (
          <Link
            key={tag.name}
            to={`/tags/${encodeURIComponent(tag.name)}`}
            className="inline-flex items-center gap-1 px-3 py-1.5 bg-white border border-gray-200 rounded-full text-sm hover:bg-blue-50 hover:border-blue-300"
          >
            <span className="text-gray-700">{tag.name}</span>
            <span className="text-xs text-gray-400">{tag.thread_count}</span>
          </Link>
        ))}
      </div>
    </div>
  )
}
