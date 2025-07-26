'use client'

import { useState, useEffect } from 'react'
import { SearchBox } from './SearchBox'
import { ProductGrid } from './ProductGrid'
import { TypewriterText } from './TypewriterText'
import { mockProducts } from '@/data/products'
import { Product, SearchState } from '@/types/product'
import { shuffleArray, debounce } from '@/lib/utils'
import { initTracker } from '@/lib/tracker';
import { useInfiniteScroll } from '@/lib/useInfiniteScroll';

export function EcommerceSearch() {
  const [searchState, setSearchState] = useState<SearchState>({
    isSearching: false,
    hasSearched: false,
    query: '',
    results: []
  })
  const { items, hasMore, lastRef } = useInfiniteScroll();

  useEffect(() => {
    initTracker();
  }, []);

  const [displayProducts, setDisplayProducts] = useState<Product[]>([])
  const [backendResponse, setBackendResponse] = useState<{
    intent: {
      title: string;
      attrs: string[];
    };
    message: string;
    status: number;
  } | null>(null)

// Initialize with shuffled products
useEffect(() => {
  setDisplayProducts(shuffleArray(mockProducts));
}, [])

  // Debounced search function
  const debouncedSearch = debounce(async (query: string) => {
    setSearchState(prev => ({ ...prev, isSearching: true }))
    
    // Simulate API call delay for both search and backend response
    await new Promise(resolve => setTimeout(resolve, 800))
    
    if (query.trim()) {
      // Filter products based on query
      const filtered = mockProducts.filter(product => 
        product.title.toLowerCase().includes(query.toLowerCase()) ||
        product.category.toLowerCase().includes(query.toLowerCase()) ||
        product.brand.toLowerCase().includes(query.toLowerCase())
      )
      
      // Simulate backend response based on query
      const mockBackendResponse = {
        intent: {
          title: query.toLowerCase().includes('jacket') || query.toLowerCase().includes('coat') 
            ? '外套系列' 
            : query.toLowerCase().includes('dress') 
            ? '連身裙系列'
            : query.toLowerCase().includes('shoes') || query.toLowerCase().includes('boot')
            ? '鞋履系列'
            : '精選商品',
          attrs: query.toLowerCase().includes('jacket') || query.toLowerCase().includes('coat')
            ? ['保暖', '防風', '時尚', '多層次']
            : query.toLowerCase().includes('dress')
            ? ['優雅', '舒適', '百搭', '氣質']
            : query.toLowerCase().includes('shoes') || query.toLowerCase().includes('boot')
            ? ['舒適', '耐磨', '時尚', '透氣']
            : ['精選', '品質', '設計', '實用']
        },
        message: `為您找到 ${filtered.length > 0 ? filtered.length : mockProducts.length} 個相關商品，根據您的搜尋「${query}」為您推薦最適合的選擇。`,
        status: 200
      }
      
      setBackendResponse(mockBackendResponse)
      
      setSearchState(prev => ({
        ...prev,
        isSearching: false,
        hasSearched: true,
        results: shuffleArray(filtered)
      }))
      
      setDisplayProducts(shuffleArray(filtered.length > 0 ? filtered : mockProducts))
    } else {
      // Clear backend response for empty queries
      setBackendResponse(null)
      
      setSearchState(prev => ({
        ...prev,
        isSearching: false,
        hasSearched: true,
        results: mockProducts
      }))
      
      setDisplayProducts(shuffleArray(mockProducts))
    }
  }, 500)

  const handleSearch = (query: string) => {
    setSearchState(prev => ({ ...prev, query, hasSearched: true }))
    debouncedSearch(query);
  
    fetch('/api/log-search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        timestamp: new Date().toISOString(),
      }),
    }).catch((err) => console.error('Failed to log search:', err))
  }
  

  const handleReset = () => {
    setSearchState({
      isSearching: false,
      hasSearched: false,
      query: '',
      results: []
    })
    setBackendResponse(null)
    setDisplayProducts(shuffleArray(mockProducts))
  }

  return (
    <div className="relative min-h-screen">
      {/* RESO */}
      <div className="absolute top-4 left-4 z-50 text-2xl font-light tracking-wider text-gray-700">
        RESO
      </div>

      {/* Background with subtle pattern */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-50 via-white to-blue-50/30" />
      
      {/* Hero section with branding */}
      {!searchState.hasSearched && (
        <div className="relative z-10 pt-20 pb-32 text-center">
          <div className="animate-fade-in">
            <h1 className="text-5xl md:text-6xl font-light text-gray-900 mb-4 tracking-tight">
              RESO
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 mb-12 font-light">
              由 AI 策劃的現代購物體驗
            </p>
          </div>
        </div>
      )}
      
      {/* Search Box */}
      <div>
        <SearchBox
          onSearch={handleSearch}
          onReset={handleReset}
          isSearching={searchState.isSearching}
          hasSearched={searchState.hasSearched}
          query={searchState.query}
        />
      </div>
      
      {/* Backend Response Display */}
      {backendResponse && searchState.hasSearched && (
        <div className="flex justify-between items-start w-full px-6 py-8 bg-gray-50 relative z-20">
          {/* 左側 Intent + tags 區塊 */}
          <div className="flex flex-col gap-4 max-w-[50%]">
            {/* Intent 圖示與文字 */}
            <div className="flex items-center gap-3 bg-white p-4 rounded-xl shadow-sm w-fit">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 text-xl">🏷️</span>
              </div>
              <span className="text-2xl font-bold text-gray-800">{backendResponse.intent.title}</span>
            </div>
            {/* 標籤群 */}
            <div className="flex flex-wrap gap-2">
              {backendResponse.intent.attrs.map((attr, index) => (
                <span
                  key={index}
                  className="text-sm bg-white text-gray-700 px-3 py-1 rounded-full shadow-sm border border-gray-200"
                >
                  {attr}
                </span>
              ))}
            </div>
          </div>

          {/* 右側 Insight 區塊 */}
          <div className="bg-white rounded-xl shadow-sm p-4 max-w-[45%] text-gray-700 leading-relaxed text-sm">
            <div className="flex items-start gap-2">
              <span className="text-purple-500 text-xl">✨</span>
              <div>
                <TypewriterText text={backendResponse.message} speed={30} />
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Products Grid */}
      {searchState.hasSearched && (
        <div className="relative z-10 pt-24 pb-32">
          <div className="container mx-auto px-4">
            <div className="mb-8 text-center">
              {/* <h2 className="text-2xl md:text-3xl font-light text-gray-900 mb-2">
                {searchState.query ? `「${searchState.query}」的搜尋結果` : '精選商品'}
              </h2> */}
              {/* <p className="text-gray-600">
                找到 {displayProducts.length} 個符合的商品
              </p> */}
            </div>
            
            <ProductGrid 
              products={displayProducts} 
              isLoading={searchState.isSearching}
              searchQuery={searchState.query}
            />
          </div>
        </div>
      )}
      
      {/* Spacer for bottom search */}
      {searchState.hasSearched && <div className="h-24" />}
    </div>
  )
}