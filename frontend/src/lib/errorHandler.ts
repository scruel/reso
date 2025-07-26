import { NextResponse } from 'next/server';

export interface ApiErrorResponse {
  success: false;
  error: {
    type: 'validation' | 'network' | 'server' | 'not_found' | 'unauthorized' | 'rate_limit' | 'unknown';
    message: string;
    details?: any;
    statusCode: number;
  };
  timestamp: string;
}

export function createErrorResponse(
  type: ApiErrorResponse['error']['type'],
  message: string,
  statusCode: number = 500,
  details?: any
): NextResponse<ApiErrorResponse> {
  const errorResponse: ApiErrorResponse = {
    success: false,
    error: {
      type,
      message,
      statusCode,
      ...(details && { details })
    },
    timestamp: new Date().toISOString()
  };

  // Log error for monitoring
  console.error(`API Error [${type}]:`, {
    message,
    statusCode,
    details,
    timestamp: errorResponse.timestamp
  });

  return NextResponse.json(errorResponse, { status: statusCode });
}

export function handleApiError(error: unknown): NextResponse<ApiErrorResponse> {
  console.error('Unhandled API error:', error);

  if (error instanceof Error) {
    // Network/Connection errors
    if (error.message.includes('ECONNREFUSED') || error.message.includes('ENOTFOUND')) {
      return createErrorResponse(
        'network',
        '無法連接到後端服務，請稍後再試',
        503,
        { originalError: error.message }
      );
    }

    // Timeout errors
    if (error.message.includes('timeout')) {
      return createErrorResponse(
        'network',
        '請求超時，請稍後再試',
        408,
        { originalError: error.message }
      );
    }

    // Validation errors
    if (error.message.includes('validation') || error.message.includes('invalid')) {
      return createErrorResponse(
        'validation',
        '請求參數無效',
        400,
        { originalError: error.message }
      );
    }

    // Generic error with message
    return createErrorResponse(
      'server',
      error.message || '內部服務器錯誤',
      500,
      { originalError: error.message }
    );
  }

  // Unknown error type
  return createErrorResponse(
    'unknown',
    '發生未知錯誤，請稍後再試',
    500,
    { originalError: String(error) }
  );
}

export function validateRequest(req: Request, requiredFields: string[]): string | null {
  const url = new URL(req.url);
  const searchParams = url.searchParams;

  for (const field of requiredFields) {
    const value = searchParams.get(field);
    if (!value || value.trim() === '') {
      return `缺少必需參數: ${field}`;
    }
  }

  return null;
}

export async function validateRequestBody(req: Request, requiredFields: string[]): Promise<{ data: any; error: string | null }> {
  try {
    const body = await req.json();
    
    for (const field of requiredFields) {
      if (!(field in body) || body[field] === undefined || body[field] === null) {
        return {
          data: null,
          error: `缺少必需參數: ${field}`
        };
      }
    }

    return { data: body, error: null };
  } catch (error) {
    return {
      data: null,
      error: '無法解析請求體，請確保發送有效的JSON'
    };
  }
}
