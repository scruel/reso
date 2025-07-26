// 新的API數據結構
export interface Good {
  id: number;
  title: string;
  pic_url: string;
  brand: string;
  category: string;
  categoryColor?: string;
  price: string;
}

export interface DChain {
  tbn_url: string;
  user_nick: string;
  user_pic_url: string;
}

export interface Thread {
  id: string;
  good: Good;
  dchain?: DChain;
}

export interface ThreadsApiResponse {
  threads: Thread[];
  status: string;
}

export interface SearchState {
  isSearching: boolean;
  hasSearched: boolean;
  query: string;
  results: Thread[];
}

// 新的產品詳情 API 響應類型
export interface ProductDetailResponse {
  title: string;
  pic_url: string;
  dchain?: {
    id: string;
    description: string;
  };
  reference_links: string;
}
