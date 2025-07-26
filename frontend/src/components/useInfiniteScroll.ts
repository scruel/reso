// src/lib/useInfiniteScroll.ts
import { useEffect, useState } from 'react'
import { Product } from '@/types/product'

const COOKIE_KEY = 'reso_uid'
const getCookie = (k: string) =>
  document.cookie.split('; ').find(row => row.startsWith(`${k}=`))?.split('=')[1]
const setCookie = (k: string, v: string, days = 7) => {
  const d = new Date()
  d.setTime(d.getTime() + days * 24 * 60 * 60 * 1000)
  document.cookie = `${k}=${v};expires=${d.toUTCString()};path=/`
}

export function useInfiniteScroll(initial: Product[]) {
  const [list, setList] = useState<Product[]>(initial)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [hasMore, setHasMore] = useState(true)

  // 保证 uuid 只生成一次
  const uid = getCookie(COOKIE_KEY) || (crypto.randomUUID() as string)
  if (!getCookie(COOKIE_KEY)) setCookie(COOKIE_KEY, uid)

  const loadMore = async () => {
    if (!hasMore || loading) return
    setLoading(true)
    const res = await fetch(`/api/products?page=${page + 1}&uid=${uid}`)
    const { data, hasMore: hm } = await res.json()
    setList(prev => [...prev, ...data])
    setPage(p => p + 1)
    setHasMore(hm)
    setLoading(false)
  }

  useEffect(() => {
    const onScroll = () => {
      if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 300)
        loadMore()
    }
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [page, hasMore, loading])

  return { list, loading, hasMore }
}