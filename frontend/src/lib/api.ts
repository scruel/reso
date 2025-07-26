// API client for thread details
export interface ThreadDetailResponse {
  title: string;
  pic_url: string;
  dchain?: {
    id: string;
    description: string;
  };
  reference_links: string;
}

export async function fetchThreadDetail(threadId: string): Promise<ThreadDetailResponse> {
  const response = await apiGet(`/api/thread?id=${threadId}`);
  
  // Transform backend response to match frontend interface
  if (response.dchain && response.dchain.descpriton) {
    response.dchain.description = response.dchain.descpriton;
    delete response.dchain.descpriton;
  }
  
  // Convert id to string if it's a number
  if (response.dchain && typeof response.dchain.id === 'number') {
    response.dchain.id = response.dchain.id.toString();
  }
  
  return response;
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
