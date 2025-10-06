import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
})

export async function fetchPosts(limit = 50, category = null) {
  try {
    const params = { limit }
    if (category) params.category = category
    const res = await client.get('/api/posts', { params })
    return res.data
  } catch (err) {
    console.error('fetchPosts failed:', err)
    throw err
  }
}

export async function analyzePosts(category = 'ai_news') {
  try {
    const res = await client.post('/api/analyze', null, { params: { category } })
    return res.data
  } catch (err) {
    console.error('analyzePosts failed:', err)
    throw err
  }
}

export async function fetchTrends() {
  try {
    const res = await client.get('/api/trends')
    return res.data
  } catch (err) {
    console.error('fetchTrends failed:', err)
    throw err
  }
}
