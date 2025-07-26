'use client'

import { useState, useEffect } from 'react'
import { SearchBox } from './SearchBox'
import { ProductGrid } from './ProductGrid'
import { TypewriterText } from './TypewriterText'
import { Sparkles } from 'lucide-react'
import { mockProducts } from '@/data/products'
import { Product, SearchState } from '@/types/product'
import { shuffleArray, debounce } from '@/lib/utils'
import { initTracker } from '@/lib/tracker';
import { useInfiniteScroll } from '@/lib/useInfiniteScroll';
import { v4 as uuidv4 } from 'uuid';

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
  // Dynamic messages that change every 5 seconds
  const dynamicMessages = [
    'Based on your search for work attire that balances packability with professional style.',
    'Analyzing fashion intent for professional occasions...',
    'AI is selecting versatile blazers for work and travel.',
    'Recommending wrinkle-resistant styles based on your taste...',
  ];
  
  const [messageIndex, setMessageIndex] = useState(0);
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

// Dynamic message switching every 5 seconds
useEffect(() => {
  const interval = setInterval(() => {
    setMessageIndex((prev) => (prev + 1) % dynamicMessages.length)
  }, 5000)

  return () => clearInterval(interval)
}, [])

// Update backend response message when index changes
useEffect(() => {
  if (backendResponse) {
    setBackendResponse((prev) => prev ? {
      ...prev,
      message: dynamicMessages[messageIndex],
    } : null)
  }
}, [messageIndex, backendResponse])

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
            ? ['保暖', '防風', '時尚', '多層次', 'Lightweight', 'Professional', 'Wrinkle-Resistant', 'Versatile']
            : query.toLowerCase().includes('dress')
            ? ['優雅', '舒適', '百搭', '氣質', 'Elegant', 'Breathable', 'Flowy', 'Feminine']
            : query.toLowerCase().includes('shoes') || query.toLowerCase().includes('boot')
            ? ['舒適', '耐磨', '時尚', '透氣', 'Durable', 'Non-slip', 'Cushioned', 'Flexible']
            : ['精選', '品質', '設計', '實用', 'Premium', 'Stylish', 'Modern', 'Essential']
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
      // Show default backend response for empty queries
      const defaultBackendResponse = {
        intent: {
          title: '精選商品',
          attrs: ['精選', '品質', '設計', '實用', 'Premium', 'Curated', 'Trending', 'Best-seller']
        },
        message: `為您精選 ${mockProducts.length} 個優質商品，涵蓋各種風格與需求。`,
        status: 200
      }
      
      setBackendResponse(defaultBackendResponse)
      
      setSearchState(prev => ({
        ...prev,
        isSearching: false,
        hasSearched: true,
        results: mockProducts
      }))
      
      setDisplayProducts(shuffleArray(mockProducts))
    }
  }, 500)

  // Async logging function with UUID
  const logUserAction = async (actionType: string, data: any = {}) => {
    const uuid = uuidv4();
    const payload = {
      uuid,
      actionType,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      ...data
    };

    try {
      // Don't await - fire and forget for better UX
      fetch('/api/log-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      }).catch((err) => console.error('Failed to log action:', err));
      
      return uuid; // Return UUID for potential use
    } catch (error) {
      console.error('Logging error:', error);
      return null;
    }
  };

  const handleSearch = (query: string) => {
    setSearchState(prev => ({ ...prev, query, hasSearched: true }))
    debouncedSearch(query);
  
    // Log search action with UUID asynchronously
    logUserAction('search', {
      query,
      searchType: query.trim() ? 'text_search' : 'empty_search'
    });
  }
  

  const handleReset = () => {
    setSearchState({
      isSearching: false,
      hasSearched: false,
      query: '',
      results: []
    })
    // Keep backend response visible after reset
    const defaultBackendResponse = {
      intent: {
        title: '精選商品',
        attrs: ['精選', '品質', '設計', '實用', 'Premium', 'Curated', 'Trending', 'Best-seller']
      },
      message: `為您精選 ${mockProducts.length} 個優質商品，涵蓋各種風格與需求。`,
      status: 200
    }
    setBackendResponse(defaultBackendResponse)
    setDisplayProducts(shuffleArray(mockProducts))
  }

  return (
    <div className="relative min-h-screen z-20">
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
        <div className="relative z-40 mt-20">
        <div className="flex justify-between items-start flex-wrap gap-6 px-6 py-8 bg-gray-50">
          {/* 左：Blazer + tags 在同一個卡片 */}
          <div className="bg-white shadow-sm rounded-xl px-6 py-4 flex flex-wrap gap-4 items-center max-w-[60%]">
            {/* Icon + Title */}
            <div className="flex items-center gap-3">
              <span className="text-4xl">🧥</span>
              <span className="text-2xl font-bold text-gray-800">{backendResponse.intent.title}</span>
            </div>
            {/* Tags */}
            <div className="flex flex-wrap gap-2">
              {backendResponse.intent.attrs.map((attr, index) => (
                <span
                  key={index}
                  className="bg-gray-100 text-gray-700 text-sm px-3 py-1 rounded-full"
                >
                  {attr}
                </span>
              ))}
            </div>
          </div>

          {/* 右：動態訊息 */}
          <div className="bg-white p-4 rounded-xl shadow-md max-w-[35%] min-w-[280px] text-sm text-gray-700 leading-relaxed flex gap-2">
            <Sparkles className="text-purple-500 mt-0.5 shrink-0" size={18} />
            <p className="transition-all duration-500">{backendResponse.message}</p>
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