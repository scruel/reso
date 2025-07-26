'use client'

import { useState, useRef, useEffect } from 'react'
import { Thread } from '@/types/product'
import { formatPrice } from '@/lib/utils'
import { Star } from 'lucide-react'
import Image from 'next/image'
import { ProductReviewPreview } from './ProductReviewPreview'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import Cookies from 'js-cookie'

interface ThreadCardProps {
  thread: Thread
  delay?: number
}

export function ProductCard({ thread, delay = 0 }: ThreadCardProps) {
  const [isImageLoaded, setIsImageLoaded] = useState(false)
  const [isImageError, setIsImageError] = useState(false)
  const [cardWidth, setCardWidth] = useState<number | undefined>(undefined)
  const cardRef = useRef<HTMLDivElement>(null)
  const router = useRouter()
  
  // 使用後端提供的顏色或預設顏色
  const categoryColor = thread.good.categoryColor || '#6B7280' // 預設為灰色

  useEffect(() => {
    if (!cardRef.current) return

    const updateWidth = () => {
      if (cardRef.current) {
        setCardWidth(cardRef.current.offsetWidth)
      }
    }

    updateWidth()

    const resizeObserver = new ResizeObserver(updateWidth)
    resizeObserver.observe(cardRef.current)

    return () => resizeObserver.disconnect()
  }, [])

  const handleClick = () => {
    console.log('ProductCard clicked, navigating to thread:', thread.id);
    
    // Log click in background
    const userUuid = Cookies.get('reso_user_uuid') || 'anonymous';
    const priceNumber = parseFloat(thread.good.price) || 0;
    const message = `用戶 ${userUuid} 點擊了商品 "${thread.good.title}" (品牌: ${thread.good.brand}, 價格: $${priceNumber.toFixed(0)})`;
    
    // 在console中打印點擊操作
    console.log(`👆 ${message}`);
    
    import('../lib/api').then(({ getApiUrl }) => {
      fetch(getApiUrl('/api/log-click'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      }).catch(() => {/* silent */});
    });
    
    // Force navigation using window.location
    if (typeof window !== 'undefined') {
      window.location.href = `/product/${thread.id}`;
    }
  }

  return (
      <div
        ref={cardRef}
        className="w-full group cursor-pointer animate-fade-in transition-transform hover:scale-[1.015]"
        style={{ animationDelay: `${delay}ms` }}
        onClick={handleClick}
      >
      <div className="rounded-2xl overflow-visible">
        {/* Top product info */}
        <div className="rounded-2xl bg-white/50 backdrop-blur-sm shadow-sm hover:shadow-lg transition-shadow duration-300 relative z-50">
          <div className="w-full h-full flex items-center justify-center text-6xl text-gray-300">
            {!isImageError ? (
              <Image
                src={thread.good.pic_url}
                alt={thread.good.title}
                width={600}
                height={600}
                className={`w-full h-auto object-cover transition-all duration-500 group-hover:scale-105 ${
                  isImageLoaded ? 'opacity-100' : 'opacity-0'
                }`}
                onLoad={() => setIsImageLoaded(true)}
                onError={() => setIsImageError(true)}
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-6xl text-gray-300">
                📦
              </div>
            )}

            {!isImageLoaded && !isImageError && (
              <div className="absolute inset-0 bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 animate-pulse" />
            )}
          </div>

          <div className="p-3">
            <div className="flex items-center justify-between mb-2">
              <span 
                className="text-[11px] font-medium px-2 py-0.5 rounded"
                style={{
                  color: categoryColor,
                  backgroundColor: `${categoryColor}15` // 15% 透明度背景
                }}
              >
                {thread.good.category}
              </span>
              <span className="text-[11px] text-gray-500">{thread.good.brand}</span>
            </div>

            <h3 className="product-title mb-2 text-sm font-medium text-gray-900 group-hover:text-primary-600 transition-colors line-clamp-2">
              {thread.good.title}
            </h3>

            <div className="flex items-center justify-between mb-3">
              <span className="text-base font-semibold text-gray-700">${parseFloat(thread.good.price).toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* 流程圖 + 作者 - 僅在有 dchain 時顯示 */}
        {thread.dchain && (
          <>
            {/* Review preview with connector */}
            {/* 細線 + 節點（疊在同一條線） */}
            {/* 線 + 節點（一條線中央有節點） */}
            <div 
              className="mx-auto w-px h-4 relative animate-fade-in"
              style={{ 
                backgroundColor: `${categoryColor}80`,
                animationDelay: `${delay}ms`
              }} // 50% 透明度的連接線
            >
              <div 
                className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full animate-fade-in"
                style={{ 
                  backgroundColor: categoryColor,
                  animationDelay: `${delay}ms`
                }} // 節點使用完整顏色
              />
            </div>

            {/* 流程圖 + 作者 */}
            <div className="bg-white/50 backdrop-blur-sm rounded-2xl shadow-sm group-hover:shadow-lg transition-shadow duration-300 overflow-hidden animate-fade-in relative" style={{ animationDelay: `${delay}ms` }}>
              <img
                src={thread.dchain.tbn_url}
                alt={`${thread.good.title} 流程示意`}
                className="w-full h-auto object-cover"
              />
              {/* Author avatar and name overlay */}
              <div className="absolute bottom-2 right-2 flex items-center gap-1.5 bg-white/90 backdrop-blur-sm rounded-full px-2 py-1 shadow-sm">
                <div className="w-5 h-5 rounded-full bg-gradient-to-br from-sky-400 to-blue-500 flex items-center justify-center text-white text-xs font-medium">
                  {thread.dchain.user_nick ? thread.dchain.user_nick.charAt(0).toUpperCase() : 'A'}
                </div>
                <span className="text-xs font-medium text-gray-700 pr-1">
                  {thread.dchain.user_nick || 'Anonymous'}
                </span>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
