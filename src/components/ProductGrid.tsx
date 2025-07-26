'use client'

import { Product } from '@/types/product'
import { ProductCard } from './ProductCard'
import { ProductCardSkeleton } from './ProductCardSkeleton'

interface ProductGridProps {
  products: Product[]
  isLoading: boolean
}

export function ProductGrid({ products, isLoading }: ProductGridProps) {
  if (isLoading) {
    return (
      <div className="columns-1 sm:columns-2 md:columns-3 lg:columns-4 gap-6">
        {Array.from({ length: 30 }).map((_, index) => (
          <div key={index} className="mb-6 break-inside-avoid">
            <ProductCardSkeleton delay={index * 50} />
          </div>
        ))}
      </div>
    )
  }

  if (products.length === 0) {
    return (
      <div className="text-center py-20">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
          <span className="text-2xl text-gray-400">🔍</span>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">沒有找到符合的商品</h3>
        <p className="text-gray-600 max-w-md mx-auto">
          請試試使用不同的關鍵詞，或瀏覽我們的精選商品系列
        </p>
      </div>
    )
  }

  return (
    <div className="columns-1 sm:columns-2 md:columns-3 lg:columns-4 gap-6">
      {products.map((product, index) => (
        <div key={product.id} className="mb-6 break-inside-avoid">
          <ProductCard product={product} delay={index * 30} />
        </div>
      ))}
    </div>
  )
}