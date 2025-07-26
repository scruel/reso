'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { ProductCard } from './ProductCard';
import { ProductCardSkeleton } from './ProductCardSkeleton';
import { Thread } from '@/types/product';
import { mockThreads } from '@/data/threads';

interface ThreadGridProps {
  products: Thread[];  // 保持products參數名稱與EcommerceSearch一致
  isLoading: boolean;
  searchQuery?: string; // 搜尋查詢
}

const INITIAL_LOAD = 30; // 初始加載數量
const LOAD_MORE = 20; // 每次加載更多數量

export function ProductGrid({ products: threads, isLoading, searchQuery }: ThreadGridProps) {
  const [displayedThreads, setDisplayedThreads] = useState<Thread[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);

  // 初始化或搜尋結果變更時重設顯示的threads
  useEffect(() => {
    if (threads.length > 0) {
      const initialThreads = threads.slice(0, INITIAL_LOAD);
      setDisplayedThreads(initialThreads);
      setHasMore(threads.length > INITIAL_LOAD);
    } else {
      setDisplayedThreads([]);
      setHasMore(false);
    }
  }, [threads]);

  // 加載更多Threads
  const loadMore = useCallback(() => {
    if (loadingMore || !hasMore) return;
    
    setLoadingMore(true);
    
    // 模擬網路延遲
    setTimeout(() => {
      const currentLength = displayedThreads.length;
      const nextThreads = threads.slice(currentLength, currentLength + LOAD_MORE);
      
      if (nextThreads.length > 0) {
        setDisplayedThreads(prev => [...prev, ...nextThreads]);
        setHasMore(currentLength + nextThreads.length < threads.length);
      } else {
        setHasMore(false);
      }
      
      setLoadingMore(false);
    }, 800); // 模擬 800ms 加載時間
  }, [displayedThreads.length, threads, loadingMore, hasMore]);

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

  // 如果正在加載且沒有threads，顯示骨架屏
  if (isLoading && displayedThreads.length === 0) {
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

  // 如果沒有threads，顯示空狀態
  if (!isLoading && displayedThreads.length === 0) {
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

  // 渲染threads網格
  return (
    <div>
      <div className="columns-1 sm:columns-2 md:columns-3 lg:columns-4 gap-6">
        {displayedThreads.map((thread, i) => (
          <div
            key={thread.id}
            className="mb-6 break-inside-avoid"
            data-thread-id={thread.id}
          >
            <ProductCard thread={thread} delay={i * 30} />
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
      
      {/* 已加載完所有threads */}
      {!hasMore && displayedThreads.length > INITIAL_LOAD && (
        <div className="text-center py-8">
          <p className="text-gray-500 text-sm">🎉 所有商品已加載完成</p>
          <p className="text-gray-400 text-xs mt-1">共 {displayedThreads.length} 個商品</p>
        </div>
      )}
    </div>
  );
}
