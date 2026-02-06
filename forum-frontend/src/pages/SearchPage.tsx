import { useQuery } from '@tanstack/react-query'
import { useSearchParams, Link } from 'react-router-dom'
import { search } from '../api/client'
import { useState } from 'react'

export default function SearchPage() {
  const [searchParams] = useSearchParams()
  const q = searchParams.get('q') || ''
  const [searchType, setSearchType] = useState<'threads' | 'posts' | 'all'>('threads')

  const results = useQuery({
    queryKey: ['search', q, searchType],
    queryFn: () => search(q, searchType),
    enabled: q.length > 0,
  })

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-900 mb-1">Search Results</h1>
      <p className="text-sm text-gray-500 mb-4">
        {q ? `Showing results for "${q}"` : 'Enter a search query'}
      </p>

      {/* Type filter */}
      <div className="flex gap-2 mb-4 text-xs">
        {(['threads', 'posts', 'all'] as const).map(t => (
          <button
            key={t}
            onClick={() => setSearchType(t)}
            className={`px-3 py-1 rounded ${searchType === t ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:bg-gray-100'}`}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {results.isLoading && <p className="text-sm text-gray-500">Searching...</p>}
      {results.error && <p className="text-sm text-red-500">Search failed</p>}

      {results.data && (
        <div className="bg-white rounded-lg border border-gray-200 divide-y divide-gray-100">
          {results.data.results.length === 0 ? (
            <p className="p-4 text-sm text-gray-500">No results found</p>
          ) : (
            results.data.results.map((result, i) => (
              <Link
                key={`${result.id}-${i}`}
                to={result.thread_id ? `/threads/${result.thread_id}` : `/threads/${result.id}`}
                className="block p-3 hover:bg-gray-50"
              >
                {result.title && (
                  <p className="text-sm font-medium text-gray-900">{result.title}</p>
                )}
                <p className="text-xs text-gray-600 mt-0.5 line-clamp-2">{result.content}</p>
                <span className="text-xs text-gray-400 mt-1 inline-block">
                  by {result.author_name}
                </span>
              </Link>
            ))
          )}
        </div>
      )}
    </div>
  )
}
