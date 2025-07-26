import { NextRequest, NextResponse } from 'next/server';

// 從其他 API 路由導入數據（在實際應用中會從數據庫獲取）
// 這裡我們需要創建一個共享的數據存儲

interface AnalyticsData {
  summary: {
    totalSearches: number;
    totalClicks: number;
    totalClientEvents: number;
    uniqueUsers: number;
    topCategories: Array<{ category: string; count: number }>;
    topSearchQueries: Array<{ query: string; count: number }>;
    topClickedProducts: Array<{ productId: string; title: string; count: number }>;
  };
  timeline: Array<{
    timestamp: string;
    searches: number;
    clicks: number;
    pageviews: number;
  }>;
  recentActivity: Array<{
    type: string;
    timestamp: string;
    details: any;
  }>;
}

export async function GET(request: NextRequest) {
  try {
    // 獲取各種日誌數據
    const baseUrl = request.url.replace('/api/analytics', '');
    
    const [searchResponse, clickResponse, clientResponse] = await Promise.all([
      fetch(`${baseUrl}/api/log-search`),
      fetch(`${baseUrl}/api/log-click`),
      fetch(`${baseUrl}/api/client-log`)
    ]);
    
    const searchData = await searchResponse.json();
    const clickData = await clickResponse.json();
    const clientData = await clientResponse.json();
    
    const searches = searchData.data || [];
    const clicks = clickData.data || [];
    const clientEvents = clientData.data || [];
    
    // 計算統計數據
    const uniqueUsers = new Set([
      ...searches.map((s: any) => s.sessionId),
      ...clicks.map((c: any) => c.sessionId),
      ...clientEvents.map((e: any) => e.userId)
    ]).size;
    
    // 統計熱門類別
    const categoryCount = clicks.reduce((acc: any, click: any) => {
      acc[click.category] = (acc[click.category] || 0) + 1;
      return acc;
    }, {});
    
    const topCategories = Object.entries(categoryCount)
      .map(([category, count]) => ({ category, count: count as number }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);
    
    // 統計熱門搜索詞
    const queryCount = searches.reduce((acc: any, search: any) => {
      if (search.query && search.query.trim()) {
        acc[search.query] = (acc[search.query] || 0) + 1;
      }
      return acc;
    }, {});
    
    const topSearchQueries = Object.entries(queryCount)
      .map(([query, count]) => ({ query, count: count as number }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);
    
    // 統計熱門商品
    const productCount = clicks.reduce((acc: any, click: any) => {
      const key = click.productId;
      if (!acc[key]) {
        acc[key] = {
          productId: click.productId,
          title: click.title,
          count: 0
        };
      }
      acc[key].count++;
      return acc;
    }, {});
    
    const topClickedProducts = Object.values(productCount)
      .sort((a: any, b: any) => b.count - a.count)
      .slice(0, 5);
    
    // 計算時間線數據（按小時統計）
    const now = new Date();
    const hoursAgo = (hours: number) => new Date(now.getTime() - hours * 60 * 60 * 1000);
    
    const timeline = Array.from({ length: 24 }, (_, i) => {
      const hourStart = hoursAgo(23 - i);
      const hourEnd = hoursAgo(22 - i);
      
      const hourSearches = searches.filter((s: any) => {
        const timestamp = new Date(s.timestamp);
        return timestamp >= hourStart && timestamp < hourEnd;
      }).length;
      
      const hourClicks = clicks.filter((c: any) => {
        const timestamp = new Date(c.timestamp);
        return timestamp >= hourStart && timestamp < hourEnd;
      }).length;
      
      const hourPageviews = clientEvents.filter((e: any) => {
        const timestamp = new Date(e.timestamp);
        return e.type === 'pageview' && timestamp >= hourStart && timestamp < hourEnd;
      }).length;
      
      return {
        timestamp: hourStart.toISOString(),
        searches: hourSearches,
        clicks: hourClicks,
        pageviews: hourPageviews
      };
    });
    
    // 最近活動
    const allEvents = [
      ...searches.map((s: any) => ({ type: 'search', timestamp: s.timestamp, details: s })),
      ...clicks.map((c: any) => ({ type: 'click', timestamp: c.timestamp, details: c })),
      ...clientEvents.filter((e: any) => e.type === 'pageview').map((e: any) => ({ 
        type: 'pageview', 
        timestamp: e.timestamp, 
        details: e 
      }))
    ].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, 20);
    
    const analyticsData: AnalyticsData = {
      summary: {
        totalSearches: searches.length,
        totalClicks: clicks.length,
        totalClientEvents: clientEvents.length,
        uniqueUsers,
        topCategories,
        topSearchQueries,
        topClickedProducts
      },
      timeline,
      recentActivity: allEvents
    };
    
    return NextResponse.json({
      success: true,
      data: analyticsData,
      generatedAt: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('分析數據錯誤:', error);
    return NextResponse.json({ 
      success: false, 
      error: 'Failed to generate analytics data' 
    }, { status: 500 });
  }
}
