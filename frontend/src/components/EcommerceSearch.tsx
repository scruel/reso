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
import StatusMessage from './StatusMessage';
import { useStatusMessage } from '@/hooks/useStatusMessage';

export function EcommerceSearch() {
  const [searchState, setSearchState] = useState<SearchState>({
    isSearching: false,
    hasSearched: false,
    query: '',
    results: []
  })
  const { items, hasMore, lastRef } = useInfiniteScroll();
  const { statusMessage, showStatusMessage, hideStatusMessage, showError, showSuccess } = useStatusMessage();

  useEffect(() => {
    initTracker();
  }, []);

  const [displayThreads, setDisplayThreads] = useState<Thread[]>([])
  // Dynamic messages that change every 5 seconds - 根據搜尋類別動態生成
  const getDynamicMessages = (query: string) => {
    const lowerQuery = query?.toLowerCase() || '';
    
    if (lowerQuery.includes('手機') || lowerQuery.includes('phone') || lowerQuery.includes('iphone')) {
      return [
        'AI正在分析您對智慧型手機的偏好與需求...',
        '基於您的搜索歷史，為您推薦最適合的手機型號...',
        '正在比較不同品牌手機的規格與性價比...',
        '根據您的使用習慣，篩選出最符合需求的手機產品...'
      ];
    }
    
    if (lowerQuery.includes('耳機') || lowerQuery.includes('headphone') || lowerQuery.includes('airpods')) {
      return [
        'AI正在分析您的音樂偏好與聆聽習慣...',
        '根據您的需求，為您推薦最適合的音頻設備...',
        '正在比較不同耳機的音質表現與降噪效果...',
        '基於您的使用場景，篩選最合適的耳機產品...'
      ];
    }
    
    if (lowerQuery.includes('筆電') || lowerQuery.includes('laptop') || lowerQuery.includes('macbook')) {
      return [
        'AI正在分析您對筆記型電腦的性能需求...',
        '根據您的工作類型，為您推薦最適合的筆電配置...',
        '正在比較不同品牌筆電的規格與續航表現...',
        '基於您的預算與需求，篩選最合適的筆電產品...'
      ];
    }
    
    if (lowerQuery.includes('遊戲') || lowerQuery.includes('gaming') || lowerQuery.includes('switch')) {
      return [
        'AI正在分析您的遊戲偏好與遊玩習慣...',
        '根據您喜愛的遊戲類型，為您推薦最適合的遊戲設備...',
        '正在比較不同遊戲平台的獨占遊戲與性能表現...',
        '基於您的遊戲需求，篩選最合適的娛樂設備...'
      ];
    }
    
    // 預設消息
    return [
      'AI正在分析您的購物偏好與需求...',
      '根據您的搜索意圖，為您推薦最適合的產品...',
      '正在比較不同產品的品質與性價比...',
      '基於您的需求，篩選最符合期望的商品...'
    ];
  };
  
  const [currentQuery, setCurrentQuery] = useState('');
  const dynamicMessages = getDynamicMessages(currentQuery);
  
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
      
      if (productsResponse && (productsResponse.threads || productsResponse.threas) && Array.isArray(productsResponse.threads || productsResponse.threas)) {
        const threadsData = productsResponse.threads || productsResponse.threas;
        let backendThreads = threadsData.map((item: any) => ({
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
        
        // 檢查是否少於30個產品，如果是則填充假數據
        if (backendThreads.length < 30) {
          const mockThreadsToAdd = mockThreads.slice(0, 30 - backendThreads.length);
          backendThreads = [...backendThreads, ...mockThreadsToAdd];
          console.log(`📦 Backend returned ${threadsData.length} products, filled with ${mockThreadsToAdd.length} mock products to reach 30`);
        }
        
        setDisplayThreads(shuffleArray(backendThreads));
        console.log(`🚀 Initialized with ${backendThreads.length} products (backend + mock fill)`);
      } else {
        setDisplayThreads(shuffleArray(mockThreads));
        console.log('🔄 Initialized with mock data - backend not available');
      }
    } catch (error: any) {
      console.error('Failed to load initial products:', error);
      showError('后端连接失败，使用模拟数据', 500);
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

  // 生成模擬的AI意圖識別響應
  const generateMockVibeResponse = (query: string, resultCount: number) => {
    const lowerQuery = query.toLowerCase();
    
    // 手機相關搜索的專門假資料
    if (lowerQuery.includes('手機') || lowerQuery.includes('phone') || lowerQuery.includes('iphone') || lowerQuery.includes('android')) {
      return {
        intent: {
          title: '智慧型手機',
          attrs: [
            '5G連網', '高解析相機', '快速充電', '大容量電池',
            '旗艦處理器', '無線充電', '防水防塵', '多鏡頭系統',
            'AI拍照', '臉部辨識', '指紋解鎖', '螢幕指紋',
            '高刷新率', 'OLED顯示', '立體聲喇叭', '遊戲模式'
          ],
          pic_url: '/images/phone-search-flowchart.png'
        },
        message: `AI分析您對「${query}」的搜尋意圖，為您精選了 ${resultCount} 款最新智慧型手機。這些產品都具備先進的拍照功能、強大的處理性能，以及出色的電池續航力，完美滿足您的日常使用需求。`,
        status: 0
      };
    }
    
    // 耳機相關搜索
    if (lowerQuery.includes('耳機') || lowerQuery.includes('headphone') || lowerQuery.includes('airpods')) {
      return {
        intent: {
          title: '高品質耳機',
          attrs: [
            '主動降噪', '高音質', '無線連接', '長續航',
            '舒適佩戴', '快速配對', '通話清晰', '運動防汗',
            '環境音模式', '觸控操作', '語音助手', '多設備連接'
          ],
          pic_url: '/images/phone-search-flowchart.png'
        },
        message: `根據您對「${query}」的搜尋，AI為您推薦 ${resultCount} 款頂級耳機產品。這些耳機都擁有卓越的音質表現、先進的降噪技術，讓您享受純淨的音樂體驗。`,
        status: 0
      };
    }
    
    // 筆電相關搜索
    if (lowerQuery.includes('筆電') || lowerQuery.includes('laptop') || lowerQuery.includes('macbook')) {
      return {
        intent: {
          title: '高效能筆記型電腦',
          attrs: [
            '輕薄設計', '長效電池', '高效處理器', '大容量記憶體',
            '快速SSD', '高解析螢幕', '多端口連接', '背光鍵盤',
            '指紋辨識', '快速開機', '靜音散熱', '專業顯卡'
          ],
          pic_url: '/images/phone-search-flowchart.png'
        },
        message: `AI理解您對「${query}」的需求，精選了 ${resultCount} 款專業筆記型電腦。這些產品結合了強大的運算能力與便攜性，適合工作、學習和娛樂等多種使用場景。`,
        status: 0
      };
    }
    
    // 遊戲相關搜索
    if (lowerQuery.includes('遊戲') || lowerQuery.includes('gaming') || lowerQuery.includes('switch') || lowerQuery.includes('ps5')) {
      return {
        intent: {
          title: '遊戲娛樂設備',
          attrs: [
            '4K遊戲', '高幀率', '快速載入', '多人遊戲',
            '手柄震動', '沉浸體驗', '豐富遊戲庫', '線上對戰',
            '便攜遊戲', '大螢幕輸出', '雲端存檔', '向下相容'
          ],
          pic_url: '/images/phone-search-flowchart.png'
        },
        message: `AI分析了您對「${query}」的興趣，為您推薦 ${resultCount} 款頂級遊戲設備。這些產品能帶來極致的遊戲體驗，讓您盡情享受各種精彩遊戲。`,
        status: 0
      };
    }
    
    // 預設響應（精選商品）
    return {
      intent: {
        title: '精選商品',
        attrs: ['精選', '品質', '設計', '實用', 'Premium', 'Stylish', 'Modern', 'Essential'],
          pic_url: '/images/phone-search-flowchart.png'
      },
      message: `為您找到 ${resultCount} 個相關商品，根據您的搜尋「${query}」為您推薦最適合的選擇。`,
      status: 0
    };
  };

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

  const handleSearch = async (query: string) => {
    setSearchState(prev => ({ ...prev, query, hasSearched: true, isSearching: true }))
    setCurrentQuery(query); // 更新当前查询，用于动态消息生成
    
    try {
      // Call real backend API for search intent
      const uuid = getUserUuid();
      const vibeResponse = await import('../lib/api').then(({ apiGet }) => 
        apiGet(`/api/vibe?query=${encodeURIComponent(query.trim() || '精選商品')}`)
      );
      
      if (vibeResponse && vibeResponse.status === 0) {
        setBackendResponse(vibeResponse);
        showSuccess('AI意图识别成功');
      } else if (vibeResponse && vibeResponse.status !== 0) {
        showError(vibeResponse.message || 'AI意图识别失败', vibeResponse.status);
      }
      
      // Get products from backend
      const productsResponse = await import('../lib/api').then(({ apiGet }) => 
        apiGet('/api/products')
      );
      
      // 检查产品API响应状态
      if (productsResponse && productsResponse.status && productsResponse.status !== 0) {
        showError(productsResponse.message || '获取产品列表失败', productsResponse.status);
      }
      
      let threadsToDisplay = mockThreads; // fallback to mock data
      if (productsResponse && (productsResponse.threads || productsResponse.threas) && Array.isArray(productsResponse.threads || productsResponse.threas)) {
        const threadsData = productsResponse.threads || productsResponse.threas;
        threadsToDisplay = threadsData.map((item: any) => ({
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
        
        if (threadsToDisplay.length < 30) {
          const mockThreadsToAdd = mockThreads.slice(0, 30 - threadsToDisplay.length);
          threadsToDisplay = [...threadsToDisplay, ...mockThreadsToAdd];
        }
      }
      
      if (query.trim()) {
        const filtered = threadsToDisplay.filter(thread => 
          thread.good.title.toLowerCase().includes(query.toLowerCase()) ||
          thread.good.category.toLowerCase().includes(query.toLowerCase()) ||
          thread.good.brand.toLowerCase().includes(query.toLowerCase())
        )
        
        // 根據搜尋詞生成不同的AI意圖識別響應
        const mockBackendResponse = generateMockVibeResponse(query, filtered.length > 0 ? filtered.length : threadsToDisplay.length)
        
        setBackendResponse(mockBackendResponse)
        setSearchState(prev => ({
          ...prev,
          isSearching: false,
          results: shuffleArray(filtered)
        }))
        setDisplayThreads(shuffleArray(filtered.length > 0 ? filtered : threadsToDisplay))
      } else {
        setSearchState(prev => ({
          ...prev,
          isSearching: false,
          results: threadsToDisplay
        }))
        setDisplayThreads(shuffleArray(threadsToDisplay))
      }
    } catch (error: any) {
      console.error('Search error:', error);
      showError('搜索过程中发生错误，使用本地数据', 500);
      
      const defaultBackendResponse = {
        intent: {
          title: '精選商品',
          attrs: ['精選', '品質', '設計', '實用'],
          pic_url: '/images/phone-search-flowchart.png'
        },
        message: `為您精選 ${mockThreads.length} 個優質商品。`,
        status: 0
      }
      
      setBackendResponse(defaultBackendResponse)
      setSearchState(prev => ({
        ...prev,
        isSearching: false,
        results: mockThreads
      }))
      setDisplayThreads(shuffleArray(mockThreads))
    }
    
    // Log search action
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
        pic_url: '/images/phone-search-flowchart.png'
      },
      message: `為您精選 ${mockThreads.length} 個優質商品，涵蓋各種風格與需求。`,
      status: 0
    }
    setBackendResponse(defaultBackendResponse)
    setDisplayThreads(shuffleArray(mockThreads))
  }

  return (
    <>
      {/* Status Message Component */}
      {statusMessage.show && (
        <StatusMessage
          status={statusMessage.status}
          message={statusMessage.message}
          show={statusMessage.show}
          onClose={hideStatusMessage}
        />
      )}
      
      {/* Light Blue Top Navigation Bar - Separate from page content */}
      <div className="fixed top-0 left-0 right-0 z-50 bg-sky-500 h-12 flex items-center">
        <div className="container mx-auto px-4 flex justify-between items-center">
          <div className="text-white text-xl font-medium tracking-wide">
            Reso
          </div>
          {/* 测试按钮 */}
          <div className="flex gap-2">
            <button 
              onClick={() => showError('测试错误消息', 500)}
              className="bg-red-500/20 text-white text-xs px-2 py-1 rounded hover:bg-red-500/30"
            >
              测试错误
            </button>
            <button 
              onClick={() => showSuccess('测试成功消息')}
              className="bg-green-500/20 text-white text-xs px-2 py-1 rounded hover:bg-green-500/30"
            >
              测试成功
            </button>
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
