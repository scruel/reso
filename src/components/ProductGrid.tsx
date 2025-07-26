'use client';

import { useEffect, useRef, useState } from 'react';
import { ProductCard } from './ProductCard';
import { ProductCardSkeleton } from './ProductCardSkeleton';
import { Product } from '@/types/product';

const LIMIT = 20;

interface ProductGridProps {
  keyword?: string; // 搜索关键字
}

export function ProductGrid({ keyword = '' }: ProductGridProps) {
  /* 瀑布流状态 */
  const [items, setItems] = useState<Product[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const observerRef = useRef<IntersectionObserver | null>(null);

  /* 向后端拿数据 */
  const fetchProducts = async (p: number, kw: string) => {
    setLoading(true);
    const res = await fetch(`/api/products?page=${p}&limit=${LIMIT}&keyword=${encodeURIComponent(kw)}`);
    const json = await res.json();
    setItems((prev) => (p === 1 ? json.products : [...prev, ...json.products]));
    setHasMore(json.hasMore);
    setLoading(false);
  };

  /* 触底触发 */
  const lastRef = (node: HTMLDivElement | null) => {
    if (observerRef.current) observerRef.current.disconnect();
    observerRef.current = new IntersectionObserver(
      ([entry]) => entry.isIntersecting && !loading && hasMore && setPage((p) => p + 1),
      { threshold: 0.5 }
    );
    if (node) observerRef.current.observe(node);
  };

  /* keyword 变化时重置 */
  useEffect(() => {
    setItems([]);
    setPage(1);
    setHasMore(true);
  }, [keyword]);

  /* 自动拉取下一页 */
  useEffect(() => {
    fetchProducts(page, keyword);
  }, [page, keyword]);

  /* 渲染 */
  if (loading && items.length === 0) {
    return (
      <div className="columns-1 sm:columns-2 md:columns-3 lg:columns-4 gap-6">
        {Array.from({ length: LIMIT }).map((_, i) => (
          <div key={i} className="mb-6 break-inside-avoid">
            <ProductCardSkeleton delay={i * 50} />
          </div>
        ))}
      </div>
    );
  }

  if (!hasMore && items.length === 0) {
    return (
      <div className="text-center py-20">
        <span className="text-2xl text-gray-400">🔍</span>
        <h3 className="text-lg font-medium text-gray-900 mt-2">沒有找到符合的商品</h3>
      </div>
    );
  }

  return (
    <div className="columns-1 sm:columns-2 md:columns-3 lg:columns-4 gap-6">
      {items.map((p, i) => (
        <div
          key={p.id}
          className="mb-6 break-inside-avoid"
          data-product-id={p.id}
          ref={i === items.length - 1 ? lastRef : null}
        >
          <ProductCard product={p} delay={i * 30} />
        </div>
      ))}
      {loading && (
        <div className="col-span-full text-center py-4">
          <div className="inline-block animate-spin rounded-full h-5 w-5 border border-orange-500 border-t-transparent" />
        </div>
      )}
    </div>
  );
}