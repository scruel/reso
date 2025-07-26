import { NextRequest, NextResponse } from 'next/server';

// 強制動態渲染
export const dynamic = 'force-dynamic';

// 模擬數據庫存儲
let searchLogs: any[] = [];

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const logEntry = {
      id: Date.now().toString(),
      query: body.query,
      timestamp: body.timestamp || new Date().toISOString(),
      userAgent: request.headers.get('user-agent'),
      ip: request.headers.get('x-forwarded-for') || 'localhost',
      sessionId: request.headers.get('x-session-id') || 'anonymous'
    };
    
    // 存儲搜索日誌
    searchLogs.push(logEntry);
    
    // 保持最近 100 筆記錄
    if (searchLogs.length > 100) {
      searchLogs = searchLogs.slice(-100);
    }
    
    console.log('🔍 搜索日誌:', logEntry);
    
    return NextResponse.json({ 
      success: true, 
      message: 'Search logged successfully',
      logId: logEntry.id
    });
  } catch (error) {
    console.error('搜索日誌錯誤:', error);
    return NextResponse.json({ 
      success: false, 
      error: 'Failed to log search' 
    }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({
    success: true,
    data: searchLogs,
    total: searchLogs.length
  });
}
