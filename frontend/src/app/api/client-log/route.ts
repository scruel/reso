import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering
export const dynamic = 'force-dynamic';

// Simulate database storage
let clientLogs: any[] = [];

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Handle batch logs (from tracker.ts)
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
      
      // Log each type of behavior with simplified message in Next.js terminal
      processedLogs.forEach(log => {
        const messages: Record<string, string> = {
          'pageview': `用戶 ${log.userId} 瀏覽了頁面`,
          'scroll': `用戶 ${log.userId} 滿動到 ${log.payload?.depth || 0}% 位置`,
          'click': `用戶 ${log.userId} 點擊了商品 ${log.payload?.productId || '未知'}`,
          'hover': `用戶 ${log.userId} 懸停在商品 ${log.payload?.productId || '未知'} 上`,
          'search': `用戶 ${log.userId} 搜索了 "${log.payload?.query || '空搜索'}"`
        };
        
        const message = messages[log.type as string] || `用戶 ${log.userId} 執行了 ${log.type} 操作`;
        console.log(`📊 ${message}`);
      });
      
      // Keep latest 200 records
      if (clientLogs.length > 200) {
        clientLogs = clientLogs.slice(-200);
      }
      
      return NextResponse.json({ 
        success: true, 
        message: `Logged ${processedLogs.length} client events`,
        count: processedLogs.length
      });
    }
    
    // Single log processing
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
    
    console.log('📊 Client log:', logEntry);
    
    return NextResponse.json({ 
      success: true, 
      message: 'Client event logged successfully',
      logId: logEntry.id
    });
  } catch (error) {
    console.error('Client log error:', error);
    return NextResponse.json({ 
      success: false, 
      error: 'Failed to log client event' 
    }, { status: 500 });
  }
}

export async function GET() {
  // Statistics for various behavior types
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
