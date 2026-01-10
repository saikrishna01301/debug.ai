'use client'

import { useEffect, useState } from 'react'

export default function Home() {
  const [apiData, setApiData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/test`)
      .then(res => res.json())
      .then(data => {
        setApiData(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching from API:', err)
        setLoading(false)
      })
  }, [])

  return (
    <main style={{ padding: '2rem', fontFamily: 'system-ui' }}>
      <h1>Welcome to DebugAI</h1>
      <p>Frontend is running on Next.js</p>

      <div style={{ marginTop: '2rem', padding: '1rem', background: '#f5f5f5', borderRadius: '8px' }}>
        <h2>API Connection Test</h2>
        {loading ? (
          <p>Loading...</p>
        ) : apiData ? (
          <pre>{JSON.stringify(apiData, null, 2)}</pre>
        ) : (
          <p>Failed to connect to API</p>
        )}
      </div>
    </main>
  )
}
