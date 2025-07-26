import { NextRequest, NextResponse } from 'next/server';

// 強制動態渲染
export const dynamic = 'force-dynamic';

// 模擬數據庫存儲
let clientLogs: any[] = [];

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // 處理批量日誌（來自 tracker.ts）
    if (Array.isArray(body)) {
      const processedLogs = body.map(log => ({
        id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: log.type,
        timestamp: new Date(log.ts).toISOString(),
        userId: log.userId,
        url: log.url,
        userAgent: log.ua,
        payload: log.payload,
        serverTimestamp: new Date().toISOString(),
        ip: request.headers.get('x-forwarded-for') || 'localhost'
      }));
      
      clientLogs.push(...processedLogs);
      
      // 記錄每種類型的行為
      processedLogs.forEach(log => {
        const emoji = {
          'pageview': '📄',
          'scroll': '📜',
          'click': '👆',
          'hover': '👀',
          'search': '🔍'
        }[log.type] || '📊';
        
        console.log(`${emoji} 客戶端行為 [${log.type}]:`, log.payload || '頁面瀏覽');
      });
      
      // 保持最近 200 筆記錄
      if (clientLogs.length > 200) {
        clientLogs = clientLogs.slice(-200);
      }
      
      return NextResponse.json({ 
        success: true, 
        message: `Logged ${processedLogs.length} client events`,
        count: processedLogs.length
      });
    }
    
    // 單一日誌處理
    const logEntry = {
      id: Date.now().toString(),
      ...body,
      serverTimestamp: new Date().toISOString(),
      ip: request.headers.get('x-forwarded-for') || 'localhost'
    };
    
    clientLogs.push(logEntry);
    
    if (clientLogs.length > 200) {
      clientLogs = clientLogs.slice(-200);
    }
    
    console.log('📊 客戶端日誌:', logEntry);
    
    return NextResponse.json({ 
      success: true, 
      message: 'Client event logged successfully',
      logId: logEntry.id
    });
  } catch (error) {
    console.error('客戶端日誌錯誤:', error);
    return NextResponse.json({ 
      success: false, 
      error: 'Failed to log client event' 
    }, { status: 500 });
  }
}

export async function GET() {
  // 統計各種行為類型
  const stats = clientLogs.reduce((acc, log) => {
    const type = log.type || 'unknown';
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  
  return NextResponse.json({
    success: true,
    data: clientLogs,
    total: clientLogs.length,
    stats
  });
}
