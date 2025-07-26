'use client'

import { useState, useEffect } from 'react'
import { SearchBox } from './SearchBox'
import { ProductGrid } from './ProductGrid'
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
        <div className="relative z-20 flex justify-between items-center mt-4 mx-8 py-4">
          <div className="flex items-center gap-4">
            <h3 className="text-lg font-semibold text-gray-900">
              {backendResponse.intent.title}
            </h3>
            <div className="flex flex-wrap gap-2">
              {backendResponse.intent.attrs.map((attr, index) => (
                <button
                  key={index}
                  className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full hover:bg-blue-200 transition-colors cursor-pointer"
                >
                  {attr}
                </button>
              ))}
            </div>
          </div>
          <div className="ml-auto bg-white rounded-lg shadow-lg border border-gray-200 p-4 max-w-md">
            <p className="text-sm text-gray-700 mb-2">{backendResponse.message}</p>
            <div className="flex justify-between items-center text-xs text-gray-500">
              <span>Status: {backendResponse.status}</span>
              <button 
                onClick={() => setBackendResponse(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
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