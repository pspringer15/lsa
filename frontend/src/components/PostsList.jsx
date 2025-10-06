import React from 'react'

const sentimentColor = (s) => {
  if (s === 'positive') return 'border-green-500/40'
  if (s === 'negative') return 'border-red-500/40'
  return 'border-amber-500/40'
}

export default function PostsList({ posts = [] }) {
  if (!posts.length) {
    return <div className="text-sm text-gray-500">No posts yet. Click "Analyze New Posts".</div>
  }

  return (
    <div className="space-y-3">
      {posts.map((p) => (
        <article key={p.id} className={`border rounded-md p-4 bg-white dark:bg-gray-800 ${sentimentColor(p.sentiment)}`}>
          {/* Post Title and Sentiment */}
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              {p.post_title ? (
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                  {p.post_url ? (
                    <a 
                      href={p.post_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                    >
                      {p.post_title}
                    </a>
                  ) : (
                    p.post_title
                  )}
                </h3>
              ) : (
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                  LinkedIn Post
                </h3>
              )}
            </div>
            <div className="text-xs uppercase tracking-wide ml-4 flex-shrink-0">
              <span className={
                p.sentiment === 'positive' ? 'text-green-600 dark:text-green-400' :
                p.sentiment === 'negative' ? 'text-red-600 dark:text-red-400' : 
                'text-amber-600 dark:text-amber-400'
              }>
                {p.sentiment} ({Math.round((p.confidence || 0) * 100)}%)
              </span>
            </div>
          </div>

          {/* Author Info - Smaller and to the right */}
          <div className="flex items-center justify-between mb-3 text-sm">
            <div className="text-xs text-gray-500">
              {p.post_date ? new Date(p.post_date).toLocaleDateString() : ''}
            </div>
            <div className="text-right">
              <div className="font-medium text-gray-700 dark:text-gray-300">
                {p.author || 'Unknown'}
              </div>
              {p.role && (
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {p.role}
                </div>
              )}
              {p.company && p.company !== p.role && (
                <div className="text-xs text-gray-500 dark:text-gray-500">
                  {p.company}
                </div>
              )}
            </div>
          </div>

          {/* Post Summary/Content */}
          <div className="text-sm text-gray-700 dark:text-gray-200 leading-relaxed border-t pt-3 dark:border-gray-700">
            {p.summary || p.content}
          </div>
        </article>
      ))}
    </div>
  )
}
