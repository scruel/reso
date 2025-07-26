'use client'

import { useState, useEffect } from 'react'
import { SearchBox } from './SearchBox'
import { ProductGrid } from './ProductGrid'
import { TypewriterText } from './TypewriterText'
import { Sparkles } from 'lucide-react'
import { mockThreads } from '@/data/threads'
import { Thread, SearchState } from '@/types/product'
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

  const [displayThreads, setDisplayThreads] = useState<Thread[]>([])
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
      pic_url?: string;
    };
    message: string;
    status: number;
  } | null>(null)

// Initialize with backend products or fallback to mock threads
useEffect(() => {
  const loadInitialProducts = async () => {
    try {
      const productsResponse = await import('../lib/api').then(({ apiGet }) => 
        apiGet('/api/products')
      );
      
      if (productsResponse && productsResponse.threads && Array.isArray(productsResponse.threads)) {
        const backendThreads = productsResponse.threads.map((item: any) => ({
          id: item.id,
          good: {
            id: item.good.id,
            title: item.good.title,
            pic_url: item.good.pic_url,
            brand: item.good.brand,
            category: item.good.category,
            categoryColor: item.good.categoryColor || '#3B82F6',
            price: item.good.price
          },
          dchain: item.dchain ? {
            tbn_url: item.dchain.tbn_url,
            user_nick: item.dchain.user_nick,
            user_pic_url: item.dchain.user_pic_url
          } : undefined
        }));
        
        setDisplayThreads(shuffleArray(backendThreads));
        console.log(`🚀 Initialized with ${backendThreads.length} products from backend`);
      } else {
        setDisplayThreads(shuffleArray(mockThreads));
        console.log('🔄 Initialized with mock data - backend not available');
      }
    } catch (error) {
      console.error('Failed to load initial products:', error);
      setDisplayThreads(shuffleArray(mockThreads));
      console.log('🔄 Initialized with mock data - backend error');
    }
  };
  
  loadInitialProducts();
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
    
    try {
      // Call real backend API for search intent
      const uuid = getUserUuid();
      const vibeResponse = await import('../lib/api').then(({ apiPost }) => 
        apiPost('/api/vibe', { uuid, query: query.trim() || '精選商品' })
      );
      
      if (vibeResponse && vibeResponse.status === 0) {
        setBackendResponse(vibeResponse);
      }
      
      // Get products from backend
      const productsResponse = await import('../lib/api').then(({ apiGet }) => 
        apiGet('/api/products')
      );
      
      let threadsToDisplay = mockThreads; // fallback to mock data
      if (productsResponse && productsResponse.threads && Array.isArray(productsResponse.threads)) {
        // Backend format matches frontend Thread format perfectly
        threadsToDisplay = productsResponse.threads.map((item: any) => ({
          id: item.id,
          good: {
            id: item.good.id,
            title: item.good.title,
            pic_url: item.good.pic_url,
            brand: item.good.brand,
            category: item.good.category,
            categoryColor: item.good.categoryColor || '#3B82F6',
            price: item.good.price
          },
          dchain: item.dchain ? {
            tbn_url: item.dchain.tbn_url,
            user_nick: item.dchain.user_nick,
            user_pic_url: item.dchain.user_pic_url
          } : undefined
        }));
        
        console.log(`📦 Loaded ${threadsToDisplay.length} products from backend`);
      } else {
        console.log('⚠️ Using fallback mock data - backend products not available');
      }
    
    if (query.trim()) {
      // Filter threads based on query
      const filtered = threadsToDisplay.filter(thread => 
        thread.good.title.toLowerCase().includes(query.toLowerCase()) ||
        thread.good.category.toLowerCase().includes(query.toLowerCase()) ||
        thread.good.brand.toLowerCase().includes(query.toLowerCase())
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
            : query.toLowerCase().includes('手機') || query.toLowerCase().includes('phone')
            ? '手機系列'
            : query.toLowerCase().includes('耳機') || query.toLowerCase().includes('headphone')
            ? '耳機系列'
            : query.toLowerCase().includes('配件') || query.toLowerCase().includes('keyboard')
            ? '配件系列'
            : '精選商品',
          attrs: query.toLowerCase().includes('jacket') || query.toLowerCase().includes('coat')
            ? ['保暖', '防風', '時尚', '多層次', 'Lightweight', 'Professional', 'Wrinkle-Resistant', 'Versatile']
            : query.toLowerCase().includes('dress')
            ? ['優雅', '舒適', '百搭', '氣質', 'Elegant', 'Breathable', 'Flowy', 'Feminine']
            : query.toLowerCase().includes('shoes') || query.toLowerCase().includes('boot')
            ? ['舒適', '耐磨', '時尚', '透氣', 'Durable', 'Non-slip', 'Cushioned', 'Flexible']
            : query.toLowerCase().includes('手機') || query.toLowerCase().includes('phone')
            ? ['高效', '創新', '智能', '便攜', 'Advanced', 'High-Performance', 'User-Friendly', 'Cutting-Edge']
            : query.toLowerCase().includes('耳機') || query.toLowerCase().includes('headphone')
            ? ['音質', '降噪', '舒適', '無線', 'Premium Audio', 'Noise-Cancelling', 'Wireless', 'Comfortable']
            : query.toLowerCase().includes('配件') || query.toLowerCase().includes('keyboard')
            ? ['效率', '人體工學', '響應', '耐用', 'Ergonomic', 'Responsive', 'Durable', 'Professional']
            : ['精選', '品質', '設計', '實用', 'Premium', 'Stylish', 'Modern', 'Essential'],
          pic_url: query.toLowerCase().includes('手機') || query.toLowerCase().includes('phone')
            ? 'https://source.unsplash.com/400x300?smartphone,technology&sig=intent1'
            : query.toLowerCase().includes('耳機') || query.toLowerCase().includes('headphone')
            ? 'https://source.unsplash.com/400x300?headphones,audio&sig=intent2'
            : query.toLowerCase().includes('配件') || query.toLowerCase().includes('keyboard')
            ? 'https://source.unsplash.com/400x300?keyboard,workspace&sig=intent3'
            : query.toLowerCase().includes('jacket') || query.toLowerCase().includes('coat')
            ? 'https://source.unsplash.com/400x300?jacket,fashion&sig=intent4'
            : 'https://source.unsplash.com/400x300?shopping,products&sig=intent5'
        },
        message: `為您找到 ${filtered.length > 0 ? filtered.length : mockThreads.length} 個相關商品，根據您的搜尋「${query}」為您推薦最適合的選擇。`,
        status: 0
      }
      
      setBackendResponse(mockBackendResponse)
      
      setSearchState(prev => ({
        ...prev,
        isSearching: false,
        hasSearched: true,
        results: shuffleArray(filtered)
      }))
      
      setDisplayThreads(shuffleArray(filtered.length > 0 ? filtered : threadsToDisplay))
    } else {
      // For empty query, show all threads from backend or fallback to mock
      setSearchState(prev => ({
        ...prev,
        isSearching: false,
        hasSearched: true,
        results: threadsToDisplay
      }))
      
      setDisplayThreads(shuffleArray(threadsToDisplay))
    }
    
    } catch (error) {
      console.error('Search error:', error);
      // Fallback to mock data and mock backend response on error
      // Show default backend response for empty queries
      const defaultBackendResponse = {
        intent: {
          title: '精選商品',
          attrs: ['精選', '品質', '設計', '實用', 'Premium', 'Curated', 'Trending', 'Best-seller'],
          pic_url: 'https://source.unsplash.com/400x300?shopping,curated&sig=default'
        },
        message: `為您精選 ${mockThreads.length} 個優質商品，涵蓋各種風格與需求。`,
        status: 0
      }
      
      setBackendResponse(defaultBackendResponse)
      
      setSearchState(prev => ({
        ...prev,
        isSearching: false,
        hasSearched: true,
        results: mockThreads
      }))
      
      setDisplayThreads(shuffleArray(mockThreads))
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
        secure: typeof window !== 'undefined' && window.location.protocol === 'https:'
      });
    }
    
    return uuid;
  };

  // Async logging function with persistent UUID
  const logUserAction = async (actionType: string, data: any = {}) => {
    const uuid = getUserUuid();
    const query = data.query || '';
    const message = query ? `用戶 ${uuid} 搜索了 "${query}"` : `用戶 ${uuid} 執行了空搜索`;

    // 在console中打印搜索操作
    console.log(`🔍 ${message}`);

    try {
      import('../lib/api').then(({ getApiUrl }) => {
        fetch(getApiUrl('/api/vibe'), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ uuid, query }),
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.status === 0) {
              setBackendResponse(data);
            }
          })
          .catch(() => {/* silent */});
      });
      
      return uuid;
    } catch (error) {
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
        attrs: ['精選', '品質', '設計', '實用', 'Premium', 'Curated', 'Trending', 'Best-seller'],
        pic_url: 'https://source.unsplash.com/400x300?shopping,curated&sig=default'
      },
      message: `為您精選 ${mockThreads.length} 個優質商品，涵蓋各種風格與需求。`,
      status: 0
    }
    setBackendResponse(defaultBackendResponse)
    setDisplayThreads(shuffleArray(mockThreads))
  }

  return (
    <>
      {/* Light Blue Top Navigation Bar - Separate from page content */}
      <div className="fixed top-0 left-0 right-0 z-50 bg-sky-500 h-12 flex items-center">
        <div className="container mx-auto px-4">
          <div className="text-white text-xl font-medium tracking-wide">
            Reso
          </div>
        </div>
      </div>

      {/* Main Page Content */}
      <div className="relative min-h-screen z-20 pt-12">
        {/* Background with subtle pattern */}
        <div className="absolute inset-0 bg-gray-100" />
      
      {/* Hero section with branding */}
      {!searchState.hasSearched && (
        <div className="relative z-10 pt-32 pb-32 text-center">
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
        <div className="relative z-20 mt-4">
          <div className="container mx-auto px-4">
            <div className="flex justify-between items-start gap-6 py-8 flex-wrap">
              {/* 左區：Title 和 Tags 水平排列 */}
              <div className="w-full max-w-[60%] flex items-start gap-4">
                {/* Title 背景卡片 - 貼合內容大小 */}
                <div className="bg-white p-4 rounded-2xl shadow-sm flex items-center gap-3 w-fit flex-shrink-0">
                  {backendResponse.intent.pic_url ? (
                    <div className="w-12 h-12 rounded-lg overflow-hidden flex-shrink-0">
                      <img 
                        src={backendResponse.intent.pic_url} 
                        alt={backendResponse.intent.title}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  ) : (
                    <div className="w-12 h-12 flex items-center justify-center text-3xl">🧥</div>
                  )}
                  <h1 className="text-2xl font-bold text-gray-800">{backendResponse.intent.title}</h1>
                </div>

                {/* Tags 水平排列並自動換行，最多顯示三行 */}
                <div className="flex flex-wrap gap-1.5 items-start max-h-[4.5rem] overflow-hidden relative flex-1">
                  {backendResponse.intent.attrs.map((tag, i) => (
                    <span
                      key={i}
                      className="bg-white text-gray-700 text-xs px-2 py-0.5 rounded border border-gray-200 whitespace-nowrap"
                    >
                      {tag}
                    </span>
                  ))}
                  {/* 省略號指示器，當內容超出時顯示 */}
                  <div className="absolute bottom-0 right-0 bg-gradient-to-l from-gray-50 via-gray-50 to-transparent pl-8 text-gray-500 text-xs">
                    {backendResponse.intent.attrs.length > 12 && '...'}
                  </div>
                </div>
              </div>

              {/* 右區：AI message 區塊 */}
              <div className="bg-white p-4 rounded-2xl shadow-sm max-w-[35%] min-w-[280px] text-sm text-gray-700 leading-relaxed flex gap-2">
                <span className="text-sky-500 text-xl">✨</span>
                <p>
                  <strong>{dynamicMessages[messageIndex]}</strong><br />
                  {backendResponse.message}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
        {/* Products Grid */}
        {searchState.hasSearched && (
          <div className="relative z-10 pt-2 pb-8">
            <div className="container mx-auto px-4">
              
              <ProductGrid 
                products={displayThreads} 
                isLoading={searchState.isSearching}
                searchQuery={searchState.query}
              />
            </div>
          </div>
        )}
        
        {/* Bottom fade overlay for dreamy effect */}
        <div className="fixed bottom-0 left-0 right-0 h-24 pointer-events-none z-30 bg-gradient-to-t from-gray-100 via-gray-100/60 to-transparent" />
        
      </div>
    </>
  )
}
