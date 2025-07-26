'use client'

import { useState, useEffect } from 'react'
import { apiGet } from '@/lib/api'

export default function TestBackendPage() {
  const [results, setResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const testEndpoint = async (endpoint: string, description: string) => {
    setLoading(true)
    try {
      console.log(`🧪 Testing: ${endpoint}`)
      const response = await apiGet(endpoint)
      console.log(`✅ Success:`, response)
      
      setResults(prev => [...prev, {
        endpoint,
        description,
        status: 'success',
        data: response,
        timestamp: new Date().toLocaleTimeString()
      }])
    } catch (err: any) {
      console.error(`❌ Error:`, err)
      setResults(prev => [...prev, {
        endpoint,
        description,
        status: 'error',
        error: err.message,
        timestamp: new Date().toLocaleTimeString()
      }])
    }
    setLoading(false)
  }

  const runTests = async () => {
    setResults([])
    setError(null)
    
    // 测试各个API端点
    await testEndpoint('/health', '健康检查')
    await testEndpoint('/api/products', '获取产品列表')
    await testEndpoint('/api/thread?tid=1', '获取产品详情 (ID: 1)')
    await testEndpoint('/api/vibe?query=手机', '意图识别 (查询: "手机")')
    await testEndpoint('/api/vibe', '意图识别 (无查询)')
  }

  useEffect(() => {
    // 页面加载时自动运行测试
    runTests()
  }, [])

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">后端API连接测试</h1>
          
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">测试状态</h2>
              <button
                onClick={runTests}
                disabled={loading}
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
              >
                {loading ? '测试中...' : '重新测试'}
              </button>
            </div>
            
            <div className="space-y-4">
              {results.map((result, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border-l-4 ${
                    result.status === 'success'
                      ? 'bg-green-50 border-green-400'
                      : 'bg-red-50 border-red-400'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className={`font-medium ${
                      result.status === 'success' ? 'text-green-800' : 'text-red-800'
                    }`}>
                      {result.description}
                    </h3>
                    <span className="text-sm text-gray-500">{result.timestamp}</span>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-2">
                    <code className="bg-gray-100 px-2 py-1 rounded">{result.endpoint}</code>
                  </p>
                  
                  {result.status === 'success' ? (
                    <div className="bg-gray-50 p-3 rounded text-sm">
                      <p className="text-green-600 font-medium mb-2">✅ 成功响应</p>
                      <pre className="text-gray-700 overflow-x-auto">
                        {JSON.stringify(result.data, null, 2)}
                      </pre>
                    </div>
                  ) : (
                    <div className="bg-gray-50 p-3 rounded text-sm">
                      <p className="text-red-600 font-medium mb-2">❌ 错误信息</p>
                      <p className="text-red-700">{result.error}</p>
                    </div>
                  )}
                </div>
              ))}
              
              {results.length === 0 && !loading && (
                <p className="text-gray-500 text-center py-8">点击"重新测试"开始API连接测试</p>
              )}
            </div>
          </div>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-medium text-blue-800 mb-2">📋 测试说明</h3>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• 后端服务器: <code>http://demo.scruel.com:8000</code></li>
              <li>• 测试包括健康检查、产品列表、产品详情和意图识别</li>
              <li>• 绿色表示成功，红色表示失败</li>
              <li>• 查看浏览器控制台获取更多调试信息</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
