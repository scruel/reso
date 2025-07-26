import { NextRequest, NextResponse } from 'next/server';

// 強制動態渲染
export const dynamic = 'force-dynamic';

// 模擬數據庫存儲
let clickLogs: any[] = [];

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const logEntry = {
      id: Date.now().toString(),
      productId: body.productId,
      title: body.title,
      brand: body.brand,
      category: body.category,
      price: body.price,
      url: body.url,
      timestamp: body.timestamp || new Date().toISOString(),
      userAgent: request.headers.get('user-agent'),
      ip: request.headers.get('x-forwarded-for') || 'localhost',
      sessionId: request.headers.get('x-session-id') || 'anonymous'
    };
    
    // 存儲點擊日誌
    clickLogs.push(logEntry);
    
    // 保持最近 100 筆記錄
    if (clickLogs.length > 100) {
      clickLogs = clickLogs.slice(-100);
    }
    
    console.log('👆 點擊日誌:', logEntry);
    
    return NextResponse.json({ 
      success: true, 
      message: 'Click logged successfully',
      logId: logEntry.id
    });
  } catch (error) {
    console.error('點擊日誌錯誤:', error);
    return NextResponse.json({ 
      success: false, 
      error: 'Failed to log click' 
    }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({
    success: true,
    data: clickLogs,
    total: clickLogs.length
  });
}
