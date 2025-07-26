'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { ExternalLink, ArrowLeft, Home, Search, AlertCircle, Wifi, Server } from 'lucide-react'
import { fetchThreadDetail, ThreadDetailResponse } from '@/lib/api'
import { mockThreads } from '@/data/threads'
import { Thread } from '@/types/product'
import { use } from 'react'

interface ProductDetailPageProps {
  params: Promise<{ id: string }>
}

type ErrorType = 'not_found' | 'network_error' | 'server_error' | 'invalid_id' | 'unknown';

interface ErrorInfo {
  type: ErrorType;
  title: string;
  message: string;
  icon: React.ComponentType<{ className?: string }>;
  suggestions: string[];
}

function getErrorInfo(error: any, id: string, thread: Thread | undefined): ErrorInfo {
  // 检查ID格式
  if (!id || id.trim() === '') {
    return {
      type: 'invalid_id',
      title: '無效的產品ID',
      message: '產品ID不能為空',
      icon: AlertCircle,
      suggestions: ['返回首頁瀏覽所有產品', '使用搜索功能查找產品']
    };
  }

  // 检查本地数据中是否存在该产品
  if (!thread) {
    return {
      type: 'not_found',
      title: '產品不存在',
      message: `找不到ID為 "${id}" 的產品`,
      icon: Search,
      suggestions: [
        '檢查產品ID是否正確',
        '返回首頁瀏覽所有產品',
        '使用搜索功能查找類似產品'
      ]
    };
  }

  // 分析具体的网络错误
  if (error) {
    const errorMessage = error.message?.toLowerCase() || '';
    
    if (errorMessage.includes('fetch') || errorMessage.includes('network') || errorMessage.includes('connect')) {
      return {
        type: 'network_error',
        title: '網絡連接錯誤',
        message: '無法連接到服務器，請檢查您的網絡連接',
        icon: Wifi,
        suggestions: [
          '檢查網絡連接是否正常',
          '刷新頁面重試',
          '稍後再試',
          '暫時查看基本產品信息'
        ]
      };
    }

    if (errorMessage.includes('500') || errorMessage.includes('server')) {
      return {
        type: 'server_error',
        title: '服務器錯誤',
        message: '服務器暫時無法處理請求',
        icon: Server,
        suggestions: [
          '稍後再試',
          '刷新頁面重試',
          '暫時查看基本產品信息',
          '聯繫客服支援'
        ]
      };
    }

    if (errorMessage.includes('404') || errorMessage.includes('not found')) {
      return {
        type: 'not_found',
        title: '產品詳情不存在',
        message: '該產品的詳細信息暫時無法獲取',
        icon: Search,
        suggestions: [
          '查看基本產品信息',
          '返回產品列表',
          '嘗試其他產品'
        ]
      };
    }
  }

  return {
    type: 'unknown',
    title: '載入失敗',
    message: '產品詳情載入時發生未知錯誤',
    icon: AlertCircle,
    suggestions: [
      '刷新頁面重試',
      '檢查網絡連接',
      '返回首頁',
      '聯繫技術支援'
    ]
  };
}

function ErrorPage({ errorInfo, thread, onRetry }: { 
  errorInfo: ErrorInfo; 
  thread?: Thread; 
  onRetry: () => void;
}) {
  const router = useRouter();
  const IconComponent = errorInfo.icon;

  return (
    <>
      {/* 頁首 Logo 導覽列 */}
      <div className="fixed top-0 left-0 right-0 z-50 bg-gray-100 backdrop-blur-sm h-12 flex items-center px-6">
        <div className="text-xl font-medium tracking-wide text-sky-600">Reso</div>
      </div>

      <div className="min-h-screen bg-gray-100 pt-12 flex items-center justify-center">
        <div className="max-w-2xl mx-auto px-4 py-8">
          <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
            {/* 錯誤圖標 */}
            <div className="mb-6">
              <div className="w-16 h-16 mx-auto bg-red-100 rounded-full flex items-center justify-center">
                <IconComponent className="w-8 h-8 text-red-500" />
              </div>
            </div>

            {/* 錯誤標題和消息 */}
            <h1 className="text-2xl font-bold text-gray-900 mb-3">{errorInfo.title}</h1>
            <p className="text-gray-600 mb-6">{errorInfo.message}</p>

            {/* 如果有基本產品信息，顯示簡化版本 */}
            {thread && errorInfo.type !== 'not_found' && (
              <div className="bg-gray-50 rounded-xl p-4 mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-2">基本產品信息</h3>
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                    <span className="text-lg">📱</span>
                  </div>
                  <div className="text-left">
                    <p className="font-medium text-gray-900">{thread.good.title}</p>
                    <p className="text-sm text-gray-500">{thread.good.brand} • {thread.good.category}</p>
                    <p className="text-sm font-medium text-blue-600">${thread.good.price}</p>
                  </div>
                </div>
              </div>
            )}

            {/* 建議操作 */}
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-700 mb-3">建議操作：</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                {errorInfo.suggestions.map((suggestion, index) => (
                  <li key={index} className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-gray-400 rounded-full flex-shrink-0" />
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>

            {/* 操作按鈕 */}
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              {(errorInfo.type === 'network_error' || errorInfo.type === 'server_error' || errorInfo.type === 'unknown') && (
                <button
                  onClick={onRetry}
                  className="px-6 py-2.5 bg-sky-500 text-white rounded-lg hover:bg-sky-600 transition-colors font-medium flex items-center justify-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  重新載入
                </button>
              )}
              
              <button
                onClick={() => router.back()}
                className="px-6 py-2.5 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors font-medium flex items-center justify-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                返回上頁
              </button>
              
              <button
                onClick={() => router.push('/')}
                className="px-6 py-2.5 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors font-medium flex items-center justify-center gap-2"
              >
                <Home className="w-4 h-4" />
                返回首頁
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default function ProductDetailPage({ params }: ProductDetailPageProps) {
  const { id } = use(params);
  const [threadDetail, setThreadDetail] = useState<ThreadDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<any>(null);
  const [retryCount, setRetryCount] = useState(0);

  // 獲取本地 thread 數據用於展示商品信息
  const thread = mockThreads.find((t) => t.id === id);
  
  // 獲取類別顏色
  const categoryColor = thread?.good.categoryColor || '#3B82F6';

  const loadThreadDetail = async (isRetry = false) => {
    try {
      if (isRetry) {
        setError(null);
      }
      setIsLoading(true);
      const detail = await fetchThreadDetail(id);
      setThreadDetail(detail);
      setRetryCount(0);
    } catch (err) {
      console.error('Failed to load thread detail:', err);
      setError(err);
      if (isRetry) {
        setRetryCount(prev => prev + 1);
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadThreadDetail();
  }, [id]);

  const handleRetry = () => {
    loadThreadDetail(true);
  };

  if (isLoading) {
    return (
      <>
        {/* 頁首 Logo 導覽列 */}
        <div className="fixed top-0 left-0 right-0 z-50 bg-gray-100 backdrop-blur-sm h-12 flex items-center px-6">
          <div className="text-xl font-medium tracking-wide text-sky-600">Reso</div>
        </div>
        
        <div className="min-h-screen bg-gray-100 pt-12 flex items-center justify-center">
          <div className="flex flex-col items-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-sky-600 border-t-transparent"></div>
            <div className="animate-pulse text-gray-500 text-lg">載入產品詳情中...</div>
            {retryCount > 0 && (
              <div className="text-sm text-gray-400">重試第 {retryCount} 次</div>
            )}
          </div>
        </div>
      </>
    );
  }

  // 如果有錯誤或無法獲取詳細信息，顯示錯誤頁面
  if (error || !threadDetail) {
    const errorInfo = getErrorInfo(error, id, thread);
    return <ErrorPage errorInfo={errorInfo} thread={thread} onRetry={handleRetry} />;
  }

  return (
    <>
      {/* 1. 頁首 Logo 導覽列（固定頂部） - 商品頁面反白樣式 */}
      <div className="fixed top-0 left-0 right-0 z-50 bg-gray-100 backdrop-blur-sm h-12 flex items-center px-6">
        <div className="text-xl font-medium tracking-wide text-sky-600">Reso</div>
      </div>

      {/* Main Content */}
      <div className="min-h-screen bg-gray-100 pt-12 flex items-center justify-center">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-4 sm:py-6 -mt-16">
          {/* 左右雙欄 Grid 排版 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8">
            
            {/* 2. 左欄：商品圖片 */}
            <div className="flex justify-center">
              <div className="w-full max-w-sm sm:max-w-md">
                <div className="bg-white rounded-2xl shadow-md overflow-hidden">
                  <div className="aspect-square relative">
                    <Image
                      src={threadDetail.pic_url}
                      alt={threadDetail.title}
                      fill
                      className="object-cover"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* 右欄：文字資訊與互動區塊 */}
            <div className="space-y-6 max-w-lg">
              {/* 3. 右欄上半區：標題與 AI Insight */}
              <div className="space-y-4">
                {/* 標題區 - 使用後端回傳的主標題 */}
                <div className="flex items-center gap-3">
                  <div className="text-3xl">🛍️</div>
                  <h1 className="text-2xl font-bold text-gray-900">{threadDetail.title}</h1>
                </div>

                {/* AI Insight 卡片 - 如果有 dchain 則顯示其 description */}
                {threadDetail.dchain && (
                  <div className="bg-white p-3 rounded-xl shadow-sm flex gap-2">
                    <span className="text-sky-500 text-lg">✨</span>
                    <p className="text-sm text-gray-600 leading-relaxed">
                      {threadDetail.dchain.description}
                    </p>
                  </div>
                )}
              </div>

              {/* 4. 右欄中段：簡單的商品資訊卡片 */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className={`grid gap-6 ${thread.dchain ? 'grid-cols-1 lg:grid-cols-2' : 'grid-cols-1'}`}>
                  {/* 左側資訊卡 */}
                  <div className="space-y-3">
                    {/* 分類和品牌 badges */}
                    <div className="flex items-center justify-between">
                      <span 
                        className="text-xs font-medium px-2 py-1 rounded-full"
                        style={{
                          color: categoryColor,
                          backgroundColor: `${categoryColor}15`
                        }}
                      >
                        {thread.good.category}
                      </span>
                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                        {thread.good.brand || 'Keychron'}
                      </span>
                    </div>

                    {/* 商品名稱 - 使用實際商品標題 */}
                    <div className="space-y-1">
                      <h2 className="text-lg font-semibold text-gray-900">
                        {thread.good.title}
                      </h2>
                      {/* 如果有副標題可以在這裡顯示 */}
                      <p className="text-sm text-gray-700">
                        {thread.good.brand} 精選商品
                      </p>
                    </div>

                    {/* 價格 */}
                    <div className="text-right">
                      <div className="text-2xl font-bold text-blue-600">
                        ${parseFloat(thread.good.price).toFixed(2)}
                      </div>
                    </div>
                  </div>

                  {/* 右側流程圖 */}
                  {thread.dchain && (
                    <div className="relative">
                      <div className="rounded-xl overflow-hidden relative">
                        <img
                          src={thread.dchain.tbn_url}
                          alt={`${thread.good.title} 使用流程`}
                          className="w-full h-auto object-cover"
                        />
                        {/* 作者資訊 badge */}
                        <div className="absolute bottom-2 right-2 flex items-center gap-2 bg-white/90 backdrop-blur-sm rounded-full px-3 py-1 shadow-sm">
                          <div className="w-5 h-5 rounded-full bg-gradient-to-br from-sky-400 to-blue-500 flex items-center justify-center text-white text-xs font-medium">
                            {thread.dchain.user_nick ? thread.dchain.user_nick.charAt(0).toUpperCase() : 'A'}
                          </div>
                          <span className="text-xs font-medium text-gray-700">
                            {thread.dchain.user_nick || 'Alex'}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* 5. 右欄下半區：購買按鈕 */}
              <div className="space-y-3">
                <button 
                  className="w-full bg-green-500 text-white text-base font-semibold px-4 py-3 rounded-lg shadow-md hover:bg-green-600 transition-colors flex items-center justify-center gap-2"
                  onClick={() => window.open(threadDetail.reference_links, '_blank')}
                >
                  <ExternalLink className="w-4 h-4" />
                  購買商品
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom fade overlay for dreamy effect */}
        <div className="fixed bottom-0 left-0 right-0 h-24 pointer-events-none z-30 bg-gradient-to-t from-gray-100 via-gray-100/60 to-transparent" />
      </div>
    </>
  );
}
