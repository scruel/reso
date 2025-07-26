export interface Product {
  id: string;
  title: string;
  price: number;
  image: string;
  category: string;
  categoryColor?: string; // 後端提供的 category 顏色
  brand: string;
  rating: number;
  url: string;

  flowImage?: string;
  author?: string;
}

export interface SearchState {
  isSearching: boolean;
  hasSearched: boolean;
  query: string;
  results: Product[];
}