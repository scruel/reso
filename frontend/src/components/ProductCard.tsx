'use client'

import { useState, useRef, useEffect } from 'react'
import { Product } from '@/types/product'
import { formatPrice } from '@/lib/utils'
import { Star } from 'lucide-react'
import Image from 'next/image'
import { ProductReviewPreview } from './ProductReviewPreview'
import * as jsCookie from 'js-cookie'

interface ProductCardProps {
  product: Product
  delay?: number
}

export function ProductCard({ product, delay = 0 }: ProductCardProps) {
  const [isImageLoaded, setIsImageLoaded] = useState(false)
  const [isImageError, setIsImageError] = useState(false)
  const [cardWidth, setCardWidth] = useState<number | undefined>(undefined)
  const cardRef = useRef<HTMLDivElement>(null)
  
  // 使用後端提供的顏色或預設顏色
  const categoryColor = product.categoryColor || '#6B7280' // 預設為灰色

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

  const handleVisit = () => {
    const userUuid = jsCookie.get('reso_user_uuid') || 'anonymous';
    fetch('/api/log-click', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        productId: product.id,
        title: product.title,
        brand: product.brand,
        category: product.category,
        price: product.price,
        url: product.url,
        timestamp: new Date().toISOString(),
        uuid: userUuid
      }),
    }).catch((err) => console.error('Failed to log click:', err))

    window.open(product.url, '_blank')
  }

  return (
    <div
      ref={cardRef}
      className="w-full group cursor-pointer animate-fade-in transition-transform hover:scale-[1.015]"
      style={{ animationDelay: `${delay}ms` }}
      onClick={handleVisit}
    >
      <div className="rounded-2xl overflow-visible">
        {/* Top product info */}
        <div className="rounded-2xl bg-white/50 backdrop-blur-sm shadow-sm relative z-10">
          <div className="w-full h-full flex items-center justify-center text-6xl text-gray-300">
            {!isImageError ? (
              <Image
                src={product.image}
                alt={product.title}
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
                {product.category}
              </span>
              <span className="text-[11px] text-gray-500">{product.brand}</span>
            </div>

            <h3 className="product-title mb-2 text-sm font-medium text-gray-900 group-hover:text-primary-600 transition-colors line-clamp-2">
              {product.title}
            </h3>

            <div className="flex items-center justify-between mb-3">
              <span className="text-base font-semibold text-gray-700">{formatPrice(product.price)}</span>
            </div>
          </div>
        </div>

        {/* Review preview with connector */}
        {/* 細線 + 節點（疊在同一條線） */}
        {/* 線 + 節點（一條線中央有節點） */}
        <div 
          className="mx-auto w-px h-4 relative"
          style={{ backgroundColor: `${categoryColor}80` }} // 50% 透明度的連接線
        >
          <div 
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full"
            style={{ backgroundColor: categoryColor }} // 節點使用完整顏色
          />
        </div>

        {/* 流程圖 + 作者 */}
        <div className="mt-2 bg-white/50 backdrop-blur-sm rounded-2xl shadow-sm overflow-hidden">
          <img
            src={product.flowImage}
            alt={`${product.title} 流程示意`}
            className="w-full h-auto object-cover"
          />
          <div className="px-3 py-2 text-sm font-semibold text-gray-800">
            by {product.author}
          </div>
        </div>
      </div>
    </div>
  )
}