'use client';

import { useEffect, useRef, useState } from 'react';
import { SearchBox } from './SearchBox';
import { ProductCard } from './ProductCard';
import { ProductCardSkeleton } from './ProductCardSkeleton';
import { mockProducts } from '@/data/products';
import { Product } from '@/types/product';

/* ---------- 1. 无限瀑布流 Hook ---------- */
const LIMIT = 20;
const useInfiniteScroll = (keyword = '') => {
  const [items, setItems] = useState<Product[]>([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const observerRef = useRef<IntersectionObserver | null>(null);

  const fetchProducts = async (p: number, kw: string) => {
    setLoading(true);
    const res = await fetch(`/api/products?page=${p}&limit=${LIMIT}&keyword=${encodeURIComponent(kw)}`);
    const json = await res.json();
    setItems((prev) => (p === 1 ? json.products : [...prev, ...json.products]));
    setHasMore(json.hasMore);
    setLoading(false);
  };

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

  /* 拉取数据 */
  useEffect(() => {
    fetchProducts(page, keyword);
  }, [page, keyword]);

  return { items, loading, hasMore, lastRef };
};

/* ---------- 2. 主组件 ---------- */
export function EcommerceSearch() {
  const [keyword, setKeyword] = useState('');
  const { items, loading, hasMore, lastRef } = useInfiniteScroll(keyword);

  return (
    <div className="relative min-h-screen">
      {/* RESO Logo */}
      <div className="absolute top-4 left-4 z-50 text-2xl font-light text-gray-700">
        RESO
      </div>

      {/* 背景 */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-50 via-white to-blue-50/30" />

      {/* 搜索框 */}
      <SearchBox
        onSearch={setKeyword}
        onReset={() => setKeyword('')}
        isSearching={loading}
        hasSearched={keyword !== ''}
        query={keyword}
      />

      {/* 无限瀑布流 */}
      <div className="container mx-auto px-4 pb-32">
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
      </div>
    </div>
  );
}