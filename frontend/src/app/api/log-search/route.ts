import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering
export const dynamic = 'force-dynamic';

// Mock database storage
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
    
    // Store search log
    searchLogs.push(logEntry);
    
    // Keep only the most recent 100 records
    if (searchLogs.length > 100) {
      searchLogs = searchLogs.slice(-100);
    }
    
    console.log('🔍 Search log:', logEntry);
    
    return NextResponse.json({ 
      success: true, 
      message: 'Search logged successfully',
      logId: logEntry.id
    });
  } catch (error) {
    console.error('Search log error:', error);
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
