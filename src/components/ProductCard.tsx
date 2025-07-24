'use client'

import { useState } from 'react'
import { Product } from '@/types/product'
import { formatPrice } from '@/lib/utils'
import { Star, ExternalLink, Heart } from 'lucide-react'
import Image from 'next/image'

interface ProductCardProps {
  product: Product
  delay?: number
}

export function ProductCard({ product, delay = 0 }: ProductCardProps) {
  const [isImageLoaded, setIsImageLoaded] = useState(false)
  const [isImageError, setIsImageError] = useState(false)
  const [isLiked, setIsLiked] = useState(false)

  const handleVisit = () => {
    // In a real app, this would navigate to the product page
    window.open(product.url, '_blank')
  }

  const handleLike = (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsLiked(!isLiked)
  }

  return (
    <div 
      className="product-card group cursor-pointer animate-fade-in"
      style={{ animationDelay: `${delay}ms` }}
      onClick={handleVisit}
    >
      {/* Product Image */}
      <div className="relative aspect-square overflow-hidden rounded-t-2xl bg-gradient-to-br from-gray-100 to-gray-200">
        {!isImageError ? (
          <Image
            src={product.image}
            alt={product.title}
            fill
            className={`object-cover transition-all duration-500 group-hover:scale-105 ${
              isImageLoaded ? 'opacity-100' : 'opacity-0'
            }`}
            onLoad={() => setIsImageLoaded(true)}
            onError={() => setIsImageError(true)}
            sizes="(max-width: 768px) 50vw, (max-width: 1024px) 33vw, (max-width: 1280px) 25vw, 20vw"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-6xl text-gray-300">
            📦
          </div>
        )}
        
        {/* Loading skeleton */}
        {!isImageLoaded && !isImageError && (
          <div className="absolute inset-0 bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 animate-pulse" />
        )}
        
        {/* Wishlist button */}
        <button
          onClick={handleLike}
          className="absolute top-3 right-3 p-2 rounded-full bg-white/80 backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-all duration-200 hover:bg-white hover:scale-110"
          title={isLiked ? '已加入心願單' : '加入心願單'}
        >
          <Heart className={`w-4 h-4 ${isLiked ? 'fill-red-500 text-red-500' : 'text-gray-600'}`} />
        </button>
        
        {/* Rating badge */}
        <div className="absolute bottom-3 left-3 flex items-center space-x-1 bg-white/90 backdrop-blur-sm px-2 py-1 rounded-lg">
          <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
          <span className="text-xs font-medium text-gray-800">{product.rating}</span>
        </div>
      </div>
      
      {/* Product Info */}
      <div className="p-4">
        {/* Category & Brand */}
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-primary-600 font-medium bg-primary-50 px-2 py-1 rounded-md">
            {product.category}
          </span>
          <span className="text-xs text-gray-500">{product.brand}</span>
        </div>
        
        {/* Title */}
        <h3 className="product-title mb-3 group-hover:text-primary-600 transition-colors">
          {product.title}
        </h3>
        
        {/* Price */}
        <div className="flex items-center justify-between mb-4">
          <span className="product-price">{formatPrice(product.price)}</span>
        </div>
        
        {/* Visit Button */}
        <button
          onClick={(e) => {
            e.stopPropagation()
            handleVisit()
          }}
          className="visit-button group/btn"
        >
          <span className="flex items-center justify-center space-x-2">
            <span>立即購買</span>
            <ExternalLink className="w-4 h-4 group-hover/btn:translate-x-0.5 transition-transform" />
          </span>
        </button>
      </div>
    </div>
  )
}