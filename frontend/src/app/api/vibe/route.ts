import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering
export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { uuid, query } = body;
    
    if (!uuid || !query) {
      return NextResponse.json(
        { error: 'UUID and query are required' },
        { status: 400 }
      );
    }
    
    console.log(`🔍 用戶 ${uuid} 搜索了 "${query}"`);
    
    // Simulate API processing delay
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // Generate response based on query content
    const generateResponse = (searchQuery: string) => {
      const lowerQuery = searchQuery.toLowerCase();
      
      // Different categories with their attributes and images
      if (lowerQuery.includes('手機') || lowerQuery.includes('phone') || lowerQuery.includes('iphone')) {
        return {
          intent: {
            title: '手機系列',
            attrs: ['高效', '創新', '智能', '便攜', 'Advanced', 'High-Performance', 'User-Friendly', 'Cutting-Edge'],
            pic_url: 'https://source.unsplash.com/400x300?smartphone,technology&sig=intent1'
          },
          message: `為您找到最新的手機產品，根據您的搜尋「${searchQuery}」為您推薦最適合的選擇。`,
          status: 0
        };
      }
      
      if (lowerQuery.includes('耳機') || lowerQuery.includes('headphone') || lowerQuery.includes('audio')) {
        return {
          intent: {
            title: '耳機系列',
            attrs: ['音質', '降噪', '舒適', '無線', 'Premium Audio', 'Noise-Cancelling', 'Wireless', 'Comfortable'],
            pic_url: 'https://source.unsplash.com/400x300?headphones,audio&sig=intent2'
          },
          message: `為您精選高品質耳機產品，根據您的搜尋「${searchQuery}」為您推薦音質絕佳的選擇。`,
          status: 0
        };
      }
      
      if (lowerQuery.includes('配件') || lowerQuery.includes('keyboard') || lowerQuery.includes('mouse')) {
        return {
          intent: {
            title: '配件系列',
            attrs: ['效率', '人體工學', '響應', '耐用', 'Ergonomic', 'Responsive', 'Durable', 'Professional'],
            pic_url: 'https://source.unsplash.com/400x300?keyboard,workspace&sig=intent3'
          },
          message: `為您推薦專業配件產品，根據您的搜尋「${searchQuery}」為您提升工作效率。`,
          status: 0
        };
      }
      
      if (lowerQuery.includes('jacket') || lowerQuery.includes('coat') || lowerQuery.includes('外套')) {
        return {
          intent: {
            title: '外套系列',
            attrs: ['保暖', '防風', '時尚', '多層次', 'Lightweight', 'Professional', 'Wrinkle-Resistant', 'Versatile'],
            pic_url: 'https://source.unsplash.com/400x300?jacket,fashion&sig=intent4'
          },
          message: `為您挑選時尚外套，根據您的搜尋「${searchQuery}」為您推薦最適合的款式。`,
          status: 0
        };
      }
      
      if (lowerQuery.includes('dress') || lowerQuery.includes('連身裙')) {
        return {
          intent: {
            title: '連身裙系列',
            attrs: ['優雅', '舒適', '百搭', '氣質', 'Elegant', 'Breathable', 'Flowy', 'Feminine'],
            pic_url: 'https://source.unsplash.com/400x300?dress,fashion&sig=intent5'
          },
          message: `為您精選優雅連身裙，根據您的搜尋「${searchQuery}」為您推薦最美的款式。`,
          status: 0
        };
      }
      
      if (lowerQuery.includes('shoes') || lowerQuery.includes('boot') || lowerQuery.includes('鞋')) {
        return {
          intent: {
            title: '鞋履系列',
            attrs: ['舒適', '耐磨', '時尚', '透氣', 'Durable', 'Non-slip', 'Cushioned', 'Flexible'],
            pic_url: 'https://source.unsplash.com/400x300?shoes,footwear&sig=intent6'
          },
          message: `為您推薦舒適鞋履，根據您的搜尋「${searchQuery}」為您找到最合適的鞋款。`,
          status: 0
        };
      }
      
      // Default response for general queries
      return {
        intent: {
          title: '精選商品',
          attrs: ['精選', '品質', '設計', '實用', 'Premium', 'Curated', 'Trending', 'Best-seller'],
          pic_url: 'https://source.unsplash.com/400x300?shopping,products&sig=intent_default'
        },
        message: `為您精選優質商品，根據您的搜尋「${searchQuery}」為您推薦最適合的選擇。`,
        status: 0
      };
    };
    
    const response = generateResponse(query);
    
    return NextResponse.json(response);
    
  } catch (error) {
    console.error('Vibe API error:', error);
    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: 'Failed to process search request',
        status: -1
      },
      { status: 500 }
    );
  }
}
