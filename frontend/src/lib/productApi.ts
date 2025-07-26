import { ProductDetailResponse } from '@/types/product';

// 模擬後端 API 調用
export async function fetchProductDetail(threadId: string): Promise<ProductDetailResponse> {
  // 在實際應用中，這裡會調用真正的 API
  // const response = await fetch(`/api/product/${threadId}`);
  // return response.json();
  
  // 使用实时数据，无需模拟延迟
  
  // 基於 threadId 返回不同的模擬數據
  const mockResponses: Record<string, ProductDetailResponse> = {
    '1': {
      title: 'Apple iPhone 15 Pro Max 256GB',
      pic_url: 'https://source.unsplash.com/600x600?smartphone,iphone&sig=1',
      dchain: {
        id: 'dchain_001',
        description: '這款 iPhone 15 Pro Max 結合了最新的 A17 Pro 晶片技術，提供出色的性能表現。48MP 主相機系統讓您捕捉每個重要時刻，而 USB-C 連接埠則帶來更便利的充電體驗。'
      },
      reference_links: 'https://www.apple.com/tw/iphone-15-pro/'
    },
    '2': {
      title: 'Keychron K8 機械鍵盤',
      pic_url: 'https://source.unsplash.com/600x600?mechanical,keyboard&sig=2',
      // 沒有 dchain
      reference_links: 'https://www.keychron.com/products/keychron-k8-wireless-mechanical-keyboard'
    },
    '3': {
      title: 'Sony WH-1000XM5',
      pic_url: 'https://source.unsplash.com/600x600?headphones,sony&sig=3',
      dchain: {
        id: 'dchain_003',
        description: 'Sony WH-1000XM5 無線降噪耳機採用先進的 V1 處理器，提供業界領先的降噪技術。30 小時的電池續航力和快速充電功能，讓您隨時享受純淨的音樂體驗。'
      },
      reference_links: 'https://www.sony.com.tw/electronics/headband-headphones/wh-1000xm5'
    },
    '4': {
      title: 'Samsung Galaxy S24 Ultra 1TB',
      pic_url: 'https://source.unsplash.com/600x600?samsung,smartphone&sig=4',
      reference_links: 'https://www.samsung.com/tw/smartphones/galaxy-s24-ultra/'
    },
    '5': {
      title: 'Sony WH-1000XM5 無線降噪耳機',
      pic_url: 'https://source.unsplash.com/600x600?headphones,wireless&sig=5',
      dchain: {
        id: 'dchain_005',
        description: '這款高端無線耳機結合了卓越的音質和智能降噪技術，無論是在通勤途中還是專注工作時，都能為您提供沉浸式的聆聽體驗。'
      },
      reference_links: 'https://www.sony.com.tw/electronics/headband-headphones/wh-1000xm5'
    }
  };
  
  const response = mockResponses[threadId];
  
  if (!response) {
    throw new Error('Product not found');
  }
  
  return response;
}
