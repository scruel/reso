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
      uuid: body.uuid || body.sessionId, // Use UUID from body
      actionType: body.actionType || 'search',
      query: body.query,
      searchType: body.searchType,
      timestamp: body.timestamp || new Date().toISOString(),
      userAgent: body.userAgent || request.headers.get('user-agent'),
      ip: request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip') || '::1',
      sessionId: body.uuid || body.sessionId || 'anonymous' // Use UUID as sessionId
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
