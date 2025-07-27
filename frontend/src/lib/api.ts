// API client for thread details
export interface ThreadDetailResponse {
  title: string;
  pic_url: string;
  price?: string;
  brand?: string;
  category?: string;
  dchain?: {
    id: string;
    description: string;
    tbn_url?: string;
    user_nick?: string;
  };
  reference_links: string;
}

export async function fetchThreadDetail(threadId: string): Promise<ThreadDetailResponse> {
  try {
    console.log('🔍 调用后端 thread API，ID:', threadId);
    const response = await apiGet(`/api/thread?tid=${threadId}`);
    console.log('📡 后端 thread API 原始响应:', response);
    
    // Check if response has status field (direct backend response)
    if (response.status !== undefined) {
      if (response.status === 0) {
        // Success response from backend
        const processedResponse = {
          title: response.title,
          pic_url: response.pic_url,
          price: response.price,
          brand: response.brand,
          category: response.category,
          reference_links: Array.isArray(response.reference_links) 
            ? response.reference_links.join(', ') 
            : response.reference_links || '',
          dchain: response.dchain ? {
            id: response.dchain.id.toString(),
            description: response.dchain.description,
            tbn_url: response.dchain.tbn_url,
            user_nick: response.dchain.user_nick
          } : undefined
        };
        console.log('✅ 后端 thread API 响应已处理:', processedResponse);
        return processedResponse;
      } else {
        // Error response from backend
        throw new Error(`Backend error: ${response.message || 'Unknown error'}`);
      }
    }
    
    // Handle new API response format (wrapped)
    if (response.success && response.data) {
      const data = response.data;
      
      // Convert id to string if it's a number
      if (data.dchain && typeof data.dchain.id === 'number') {
        data.dchain.id = data.dchain.id.toString();
      }
      
      return data;
    }
    
    // Handle old format for backward compatibility
    if (!response.success && !response.error) {
      // Convert id to string if it's a number
      if (response.dchain && typeof response.dchain.id === 'number') {
        response.dchain.id = response.dchain.id.toString();
      }
      
      return response;
    }
    
    // Handle error response
    if (response.error) {
      const error = new Error(response.error.message || 'API錯誤');
      error.name = response.error.type || 'ApiError';
      throw error;
    }
    
    throw new Error('無效的API響應格式');
    
  } catch (error) {
    console.error('Failed to fetch thread detail:', error);
    throw error;
  }
}

// API utility functions with environment variable support

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://demo.scruel.com:8000';

export const getApiUrl = (endpoint: string): string => {
  // Check if endpoint is for backend services
  if (endpoint.startsWith('/api/vibe') || endpoint.startsWith('/api/thread') || endpoint.startsWith('/api/products')) {
    // Use backend server for these endpoints
    return `${API_BASE_URL}${endpoint}`;
  }
  // Use Next.js API routes for logging endpoints
  return endpoint;
};

export const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
  const url = getApiUrl(endpoint);
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API request failed for ${url}:`, error);
    throw error;
  }
};

// Convenience methods
export const apiGet = (endpoint: string) => apiRequest(endpoint, { method: 'GET' });

export const apiPost = (endpoint: string, data: any) => 
  apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  });

export const apiPut = (endpoint: string, data: any) => 
  apiRequest(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data),
  });

export const apiDelete = (endpoint: string) => 
  apiRequest(endpoint, { method: 'DELETE' });
