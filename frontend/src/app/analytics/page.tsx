'use client'

import { useState, useEffect } from 'react'

interface AnalyticsData {
  summary: {
    totalSearches: number
    totalClicks: number
    totalClientEvents: number
    uniqueUsers: number
    topCategories: Array<{ category: string; count: number }>
    topSearchQueries: Array<{ query: string; count: number }>
    topClickedProducts: Array<{ productId: string; title: string; count: number }>
  }
  timeline: Array<{
    timestamp: string
    searches: number
    clicks: number
    pageviews: number
  }>
  recentActivity: Array<{
    type: string
    timestamp: string
    details: any
  }>
}

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    try {
      const response = await fetch('/api/analytics')
      const result = await response.json()
      
      if (result.success) {
        setData(result.data)
      } else {
        setError(result.error)
      }
    } catch (err) {
      setError('Failed to fetch analytics data')
    } finally {
      setLoading(false)
    }
  }

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('zh-TW')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加載分析數據中...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            重新加載
          </button>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">沒有數據</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">📊 RESO 分析儀表板</h1>
          <p className="mt-2 text-gray-600">用戶行為數據分析</p>
          <button 
            onClick={fetchAnalytics}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            🔄 刷新數據
          </button>
        </div>

        {/* 總覽統計 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">總搜索次數</h3>
            <p className="text-2xl font-bold text-blue-600">{data.summary.totalSearches}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">總點擊次數</h3>
            <p className="text-2xl font-bold text-green-600">{data.summary.totalClicks}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">用戶行為事件</h3>
            <p className="text-2xl font-bold text-purple-600">{data.summary.totalClientEvents}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">獨立用戶</h3>
            <p className="text-2xl font-bold text-orange-600">{data.summary.uniqueUsers}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* 熱門搜索詞 */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">🔍 熱門搜索詞</h3>
            {data.summary.topSearchQueries.length > 0 ? (
              <div className="space-y-2">
                {data.summary.topSearchQueries.map((item, index) => (
                  <div key={item.query} className="flex justify-between items-center">
                    <span className="text-gray-700">{index + 1}. {item.query}</span>
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">{item.count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">暫無搜索數據</p>
            )}
          </div>

          {/* 熱門類別 */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">📱 熱門類別</h3>
            {data.summary.topCategories.length > 0 ? (
              <div className="space-y-2">
                {data.summary.topCategories.map((item, index) => (
                  <div key={item.category} className="flex justify-between items-center">
                    <span className="text-gray-700">{index + 1}. {item.category}</span>
                    <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">{item.count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">暫無類別數據</p>
            )}
          </div>
        </div>

        {/* 熱門商品 */}
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🛍️ 熱門商品</h3>
          {data.summary.topClickedProducts.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.summary.topClickedProducts.map((item, index) => (
                <div key={item.productId} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-medium text-gray-900">#{index + 1}</span>
                    <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-sm">{item.count} 次點擊</span>
                  </div>
                  <p className="text-gray-700 text-sm">{item.title}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">暫無商品點擊數據</p>
          )}
        </div>

        {/* 最近活動 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">⏰ 最近活動</h3>
          {data.recentActivity.length > 0 ? (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {data.recentActivity.map((activity, index) => {
                const emoji = {
                  'search': '🔍',
                  'click': '👆',
                  'pageview': '📄'
                }[activity.type] || '📊'
                
                return (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded">
                    <span className="text-lg">{emoji}</span>
                    <div className="flex-1">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {activity.type === 'search' && `搜索: "${activity.details.query}"`}
                            {activity.type === 'click' && `點擊: ${activity.details.title}`}
                            {activity.type === 'pageview' && '頁面瀏覽'}
                          </p>
                          <p className="text-xs text-gray-500">{formatTime(activity.timestamp)}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <p className="text-gray-500">暫無最近活動</p>
          )}
        </div>

        <div className="mt-8 text-center text-gray-500 text-sm">
          <p>數據每次頁面加載時更新 • 開發測試環境</p>
        </div>
      </div>
    </div>
  )
}
