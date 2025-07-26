import { NextRequest, NextResponse } from 'next/server';

// Mock data that simulates the new backend API response format
const mockThreadDetails: Record<string, any> = {
  '1': {
    title: 'Apple iPhone 15 Pro Max 256GB',
    pic_url: 'https://source.unsplash.com/random/400x400?sig=1',
    dchain: {
      id: 'dchain_1',
      description: '根據用戶評價和專家測試，這款 iPhone 15 Pro Max 在拍照、性能和電池壽命方面表現卓越，特別適合專業用戶和攝影愛好者。'
    },
    reference_links: 'https://www.apple.com/tw/iphone-15-pro/'
  },
  '2': {
    title: 'Keychron K8 機械鍵盤',
    pic_url: 'https://source.unsplash.com/random/400x400?sig=2',
    // No dchain for this product
    reference_links: 'https://www.keychron.com/products/keychron-k8-wireless-mechanical-keyboard'
  },
  '3': {
    title: 'Sony WH-1000XM5',
    pic_url: 'https://source.unsplash.com/random/400x400?sig=3',
    dchain: {
      id: 'dchain_3',
      description: 'Sony WH-1000XM5 憑藉其業界領先的降噪技術和優質音質，成為商務人士和音樂愛好者的首選。電池續航力可達30小時，適合長途旅行使用。'
    },
    reference_links: 'https://electronics.sony.com/audio/headphones/headband/p/wh1000xm5-b'
  },
  '4': {
    title: 'Samsung Galaxy S24 Ultra 1TB',
    pic_url: 'https://images.samsung.com/is/image/samsung/p6pim/ph/sm-s928bzgcphl/gallery/ph-galaxy-s24-ultra-s928-sm-s928bzgcphl-thumb-539711237',
    reference_links: 'https://www.samsung.com/tw/smartphones/galaxy-s24-ultra/'
  },
  '5': {
    title: 'Sony WH-1000XM5 無線降噪耳機',
    pic_url: 'https://m.media-amazon.com/images/I/61KPF+Zxj-L._AC_SL1500_.jpg',
    dchain: {
      id: 'dchain_5',
      description: '這款耳機搭載 V1 處理器和雙噪音感測器技術，提供卓越的降噪體驗。LDAC 技術確保高解析度音質傳輸，讓您享受更豐富的音樂細節。'
    },
    reference_links: 'https://www.sony.com.tw/electronics/headband-headphones/wh-1000xm5'
  }
};

export async function GET(request: NextRequest) {
  // Get the thread ID from query parameters
  const { searchParams } = new URL(request.url);
  const id = searchParams.get('id');
  
  if (!id) {
    return NextResponse.json(
      { error: 'Thread ID is required as query parameter' },
      { status: 400 }
    );
  }
  
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  const threadDetail = mockThreadDetails[id];
  
  if (!threadDetail) {
    return NextResponse.json(
      { error: 'Thread not found' },
      { status: 404 }
    );
  }
  
  return NextResponse.json(threadDetail);
}
