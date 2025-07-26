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
import Cookies from 'js-cookie';

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

  // Get or create persistent user UUID
  const getUserUuid = () => {
    const COOKIE_KEY = 'reso_user_uuid';
    let uuid = Cookies.get(COOKIE_KEY);
    
    if (!uuid) {
      uuid = uuidv4();
      // Set cookie to expire in 1 year
      Cookies.set(COOKIE_KEY, uuid, { 
        expires: 365, 
        sameSite: 'Lax',
        secure: window.location.protocol === 'https:'
      });
    }
    
    return uuid;
  };

  // Async logging function with persistent UUID
  const logUserAction = async (actionType: string, data: any = {}) => {
    const uuid = getUserUuid(); // Use persistent UUID
    const payload = {
      uuid,
      actionType,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      sessionId: uuid, // Use same UUID as session ID
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
      <div className="absolute top-2 left-8 z-50 text-2xl font-light tracking-wider text-gray-700">
        RESO
      </div>

      {/* Background with subtle pattern */}
      <div className="absolute inset-0 bg-gray-100" />
      
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
        <div className="relative z-40 mt-4">
          <div className="flex justify-between items-start gap-6 px-6 py-8 flex-wrap">
            {/* 左區：Title + Tags 區塊 */}
            <div className="px-6 py-4 w-full max-w-[60%] flex items-start gap-6">
              {/* 左側：Icon + Title 水平排列 */}
              <div className="flex-shrink-0 flex items-center gap-3">
                <div className="w-12 h-12 flex items-center justify-center text-3xl">🧥</div>
                <h1 className="text-2xl font-bold text-gray-800">{backendResponse.intent.title}</h1>
              </div>

              {/* 右側：Tags 水平排列並自動換行 */}
              <div className="flex flex-wrap gap-2 items-start pt-1">
                {backendResponse.intent.attrs.map((tag, i) => (
                  <span
                    key={i}
                    className="bg-white text-gray-700 text-xs px-3 py-1 rounded-md"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            {/* 右區：AI message 區塊 */}
            <div className="bg-white p-4 rounded-2xl shadow-sm max-w-[35%] min-w-[280px] text-sm text-gray-700 leading-relaxed flex gap-2">
              <span className="text-purple-500 text-xl">✨</span>
              <p>
                <strong>{dynamicMessages[messageIndex]}</strong><br />
                {backendResponse.message}
              </p>
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