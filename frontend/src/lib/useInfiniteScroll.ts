/* lib/useInfiniteScroll.ts */
import { useEffect, useRef, useState } from 'react';
import { mockProducts } from '@/data/products';
import { Product } from '@/types/product';

export const PAGE_SIZE = 20;

export const useInfiniteScroll = () => {
  const [items, setItems] = useState<Product[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const observerRef = useRef<IntersectionObserver | null>(null);

  const loadMore = () => {
    if (!hasMore) return;
    const start = (page - 1) * PAGE_SIZE;
    const end = start + PAGE_SIZE;
    const next = mockProducts.slice(start, end);
    setItems((prev) => [...prev, ...next]);
    setPage((p) => p + 1);
    setHasMore(end < mockProducts.length);
  };

  const lastRef = (node: HTMLDivElement | null) => {
    if (observerRef.current) observerRef.current.disconnect();
    observerRef.current = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) loadMore();
      },
      { threshold: 0.5 }
    );
    if (node) observerRef.current.observe(node);
  };

  return { items, hasMore, lastRef };
};