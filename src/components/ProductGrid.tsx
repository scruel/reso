'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { ProductCard } from './ProductCard';
import { ProductCardSkeleton } from './ProductCardSkeleton';
import { Product } from '@/types/product';
import { mockProducts } from '@/data/products';

interface ProductGridProps {
  products: Product[];
  isLoading: boolean;
  searchQuery?: string; // 搜尋查詢
}

const INITIAL_LOAD = 30; // 初始加載數量
const LOAD_MORE = 20; // 每次加載更多數量

export function ProductGrid({ products, isLoading, searchQuery }: ProductGridProps) {
  const [displayedProducts, setDisplayedProducts] = useState<Product[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);

  // 初始化或搜尋結果變更時重設顯示的商品
  useEffect(() => {
    if (products.length > 0) {
      const initialProducts = products.slice(0, INITIAL_LOAD);
      setDisplayedProducts(initialProducts);
      setHasMore(products.length > INITIAL_LOAD);
    } else {
      setDisplayedProducts([]);
      setHasMore(false);
    }
  }, [products]);

  // 加載更多商品
  const loadMore = useCallback(() => {
    if (loadingMore || !hasMore) return;
    
    setLoadingMore(true);
    
    // 模擬網絡延遲
    setTimeout(() => {
      const currentLength = displayedProducts.length;
      const nextProducts = products.slice(currentLength, currentLength + LOAD_MORE);
      
      if (nextProducts.length > 0) {
        setDisplayedProducts(prev => [...prev, ...nextProducts]);
        setHasMore(currentLength + nextProducts.length < products.length);
      } else {
        setHasMore(false);
      }
      
      setLoadingMore(false);
    }, 800); // 模擬 800ms 加載時間
  }, [displayedProducts.length, products, loadingMore, hasMore]);

  // 設置 Intersection Observer
  useEffect(() => {
    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    observerRef.current = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !loadingMore) {
          loadMore();
        }
      },
      { threshold: 0.1 }
    );

    if (loadMoreRef.current) {
      observerRef.current.observe(loadMoreRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [hasMore, loadingMore, loadMore]);

  // 如果正在加載且沒有商品，顯示骨架屏
  if (isLoading && displayedProducts.length === 0) {
    return (
      <div className="columns-1 sm:columns-2 md:columns-3 lg:columns-4 gap-6">
        {Array.from({ length: INITIAL_LOAD }).map((_, i) => (
          <div key={i} className="mb-6 break-inside-avoid">
            <ProductCardSkeleton delay={i * 50} />
          </div>
        ))}
      </div>
    );
  }

  // 如果沒有商品，顯示空狀態
  if (!isLoading && displayedProducts.length === 0) {
    return (
      <div className="text-center py-20">
        <span className="text-2xl text-gray-400">🔍</span>
        <h3 className="text-lg font-medium text-gray-900 mt-2">沒有找到符合的商品</h3>
        {searchQuery && (
          <p className="text-gray-500 mt-1">試試使用不同的關鍵字</p>
        )}
      </div>
    );
  }

  // 渲染商品網格
  return (
    <div>
      <div className="columns-1 sm:columns-2 md:columns-3 lg:columns-4 gap-6">
        {displayedProducts.map((product, i) => (
          <div
            key={product.id}
            className="mb-6 break-inside-avoid"
            data-product-id={product.id}
          >
            <ProductCard product={product} delay={i * 30} />
          </div>
        ))}
      </div>
      
      {/* 加載更多觸發器 */}
      {hasMore && (
        <div 
          ref={loadMoreRef}
          className="flex justify-center py-8"
        >
          {loadingMore ? (
            <div className="flex flex-col items-center space-y-4">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-2 border-orange-500 border-t-transparent" />
              <p className="text-gray-500 text-sm">加載中...</p>
            </div>
          ) : (
            <div className="text-gray-400 text-sm">向下滾動查看更多商品</div>
          )}
        </div>
      )}
      
      {/* 已加載完所有商品 */}
      {!hasMore && displayedProducts.length > INITIAL_LOAD && (
        <div className="text-center py-8">
          <p className="text-gray-500 text-sm">🎉 所有商品已加載完成</p>
          <p className="text-gray-400 text-xs mt-1">共 {displayedProducts.length} 個商品</p>
        </div>
      )}
    </div>
  );
}
