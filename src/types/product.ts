export interface Product {
  id: string;
  title: string;
  price: number;
  image: string;
  category: string;
  brand: string;
  rating: number;
  url: string;
}

export interface SearchState {
  isSearching: boolean;
  hasSearched: boolean;
  query: string;
  results: Product[];
}