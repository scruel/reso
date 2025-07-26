'use client';

import { ProductCard } from './ProductCard';
import { ProductCardSkeleton } from './ProductCardSkeleton';
import { Product } from '@/types/product';

interface ProductGridProps {
  products: Product[];
  isLoading: boolean;
}

export function ProductGrid({ products, isLoading }: ProductGridProps) {
  // 如果正在加載且沒有商品，顯示骨架屏
  if (isLoading && products.length === 0) {
    return (
      <div className="columns-1 sm:columns-2 md:columns-3 lg:columns-4 gap-6">
        {Array.from({ length: 12 }).map((_, i) => (
          <div key={i} className="mb-6 break-inside-avoid">
            <ProductCardSkeleton delay={i * 50} />
          </div>
        ))}
      </div>
    );
  }

  // 如果沒有商品，顯示空狀態
  if (!isLoading && products.length === 0) {
    return (
      <div className="text-center py-20">
        <span className="text-2xl text-gray-400">🔍</span>
        <h3 className="text-lg font-medium text-gray-900 mt-2">沒有找到符合的商品</h3>
      </div>
    );
  }

  // 渲染商品網格
  return (
    <div className="columns-1 sm:columns-2 md:columns-3 lg:columns-4 gap-6">
      {products.map((product, i) => (
        <div
          key={product.id}
          className="mb-6 break-inside-avoid"
          data-product-id={product.id}
        >
          <ProductCard product={product} delay={i * 30} />
        </div>
      ))}
      {isLoading && (
        <div className="col-span-full text-center py-4">
          <div className="inline-block animate-spin rounded-full h-5 w-5 border border-orange-500 border-t-transparent" />
        </div>
      )}
    </div>
  );
}
