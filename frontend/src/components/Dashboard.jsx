import React, { useEffect, useState } from 'react'
import { fetchPosts, analyzePosts, fetchTrends } from '../services/api.js'
import PostsList from './PostsList.jsx'

export default function Dashboard() {
  const [posts, setPosts] = useState([])
  const [trends, setTrends] = useState(null)
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState(null)
  const [dark, setDark] = useState(true)
  const [category, setCategory] = useState('ai_news')

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
  }, [dark])

  useEffect(() => {
    const run = async () => {
      setLoading(true)
      setError(null)
      try {
        const [p, t] = await Promise.all([fetchPosts(50, category), fetchTrends()])
        setPosts(p || [])
        setTrends(t || null)
      } catch (e) {
        setError('Unable to load data')
      } finally {
        setLoading(false)
      }
    }
    run()
  }, [category])

  const handleAnalyze = async () => {
    setAnalyzing(true)
    setError(null)
    try {
      await analyzePosts(category)
      const [p, t] = await Promise.all([fetchPosts(50, category), fetchTrends()])
      setPosts(p || [])
      setTrends(t || null)
    } catch (e) {
      setError('Analysis failed')
      console.error(e)
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <div className="min-h-screen text-gray-900 dark:text-gray-100">
      <header className="border-b border-gray-200 dark:border-gray-800 bg-white/70 dark:bg-gray-900/70 backdrop-blur sticky top-0">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl sm:text-2xl font-semibold">LinkedIn Sentiment Tracker</h1>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setDark(d => !d)}
                className="px-3 py-2 rounded-md text-sm border border-gray-300 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800"
              >
                {dark ? 'Light' : 'Dark'} Mode
              </button>
              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                className="px-4 py-2 rounded-md text-sm bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60"
              >
                {analyzing ? 'Analyzing…' : 'Analyze New Posts'}
              </button>
            </div>
          </div>
          
          {/* Category Tabs */}
          <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setCategory('ai_news')}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                category === 'ai_news'
                  ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              AI News
            </button>
            <button
              onClick={() => setCategory('career_advice')}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                category === 'career_advice'
                  ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              Career Advice
            </button>
            <button
              onClick={() => setCategory('new_research')}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                category === 'new_research'
                  ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              New Research
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-4 space-y-6">
        {error && (
          <div className="card border border-red-500/40">
            <div className="text-red-400 font-medium">Error</div>
            <div className="text-sm">{error}</div>
          </div>
        )}

        <section>
          <div className="card overflow-y-auto" style={{ maxHeight: '70vh' }}>
            <div className="mb-4">
              <div className="text-lg font-semibold mb-1">
                {category === 'ai_news' && 'AI News & Model Comparisons'}
                {category === 'career_advice' && 'Career & Job Advice'}
                {category === 'new_research' && 'New Research & Papers'}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {category === 'ai_news' && 'Latest updates on ChatGPT, Claude, Perplexity, Grok, and other AI models'}
                {category === 'career_advice' && 'Interview tips and engineering advice from rajya-vardhan, sanchitnarula, tannika-majumder, debarghyadas'}
                {category === 'new_research' && 'ArXiv papers and algorithm breakthroughs in AI/ML'}
              </div>
            </div>
            {loading ? (
              <div className="text-sm text-gray-500">Loading…</div>
            ) : posts.length === 0 ? (
              <div className="text-sm text-gray-500">
                No posts found. Click "Analyze New Posts" to fetch and analyze posts for this category.
              </div>
            ) : (
              <PostsList posts={posts} />
            )}
          </div>
        </section>
      </main>
    </div>
  )
}
