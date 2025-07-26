'use client'

import { useState, useEffect } from 'react'
import { notFound } from 'next/navigation'
import Image from 'next/image'
import { ExternalLink } from 'lucide-react'
import { fetchThreadDetail, ThreadDetailResponse } from '@/lib/api'
import { mockThreads } from '@/data/threads'
import { Thread } from '@/types/product'
import { use } from 'react'

interface ProductDetailPageProps {
  params: Promise<{ id: string }>
}

export default function ProductDetailPage({ params }: ProductDetailPageProps) {
  const { id } = use(params);
  const [threadDetail, setThreadDetail] = useState<ThreadDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 獲取本地 thread 數據用於展示商品信息
  const thread = mockThreads.find((t) => t.id === id);
  
  // 獲取類別顏色
  const categoryColor = thread?.good.categoryColor || '#3B82F6';

  useEffect(() => {
    const loadThreadDetail = async () => {
      try {
        setIsLoading(true);
        const detail = await fetchThreadDetail(id);
        setThreadDetail(detail);
      } catch (err) {
        console.error('Failed to load thread detail:', err);
        setError('產品不存在或載入失敗');
      } finally {
        setIsLoading(false);
      }
    };

    loadThreadDetail();
  }, [id]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-sky-600 border-t-transparent"></div>
          <div className="animate-pulse text-gray-500 text-lg">載入中...</div>
        </div>
      </div>
    );
  }

  if (error || !threadDetail || !thread) {
    return notFound();
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
