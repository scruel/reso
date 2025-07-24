'use client'

import { useState, useEffect } from 'react'
import { SearchBox } from './SearchBox'
import { ProductGrid } from './ProductGrid'
import { mockProducts } from '@/data/products'
import { Product, SearchState } from '@/types/product'
import { shuffleArray, debounce } from '@/lib/utils'

export function EcommerceSearch() {
  const [searchState, setSearchState] = useState<SearchState>({
    isSearching: false,
    hasSearched: false,
    query: '',
    results: []
  })

  const [displayProducts, setDisplayProducts] = useState<Product[]>([])

  // Initialize with shuffled products
  useEffect(() => {
    setDisplayProducts(shuffleArray(mockProducts))
  }, [])

  // Debounced search function
  const debouncedSearch = debounce(async (query: string) => {
    setSearchState(prev => ({ ...prev, isSearching: true }))
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 800))
    
    if (query.trim()) {
      // Filter products based on query
      const filtered = mockProducts.filter(product => 
        product.title.toLowerCase().includes(query.toLowerCase()) ||
        product.category.toLowerCase().includes(query.toLowerCase()) ||
        product.brand.toLowerCase().includes(query.toLowerCase())
      )
      
      setSearchState(prev => ({
        ...prev,
        isSearching: false,
        hasSearched: true,
        results: shuffleArray(filtered)
      }))
      
      setDisplayProducts(shuffleArray(filtered.length > 0 ? filtered : mockProducts))
    } else {
      setSearchState(prev => ({
        ...prev,
        isSearching: false,
        hasSearched: true,
        results: mockProducts
      }))
      
      setDisplayProducts(shuffleArray(mockProducts))
    }
  }, 500)

  const handleSearch = (query: string) => {
    setSearchState(prev => ({ ...prev, query, hasSearched: true }))
    debouncedSearch(query)
  }

  const handleReset = () => {
    setSearchState({
      isSearching: false,
      hasSearched: false,
      query: '',
      results: []
    })
    setDisplayProducts(shuffleArray(mockProducts))
  }

  return (
    <div className="relative min-h-screen">
      {/* Background with subtle pattern */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-50 via-white to-blue-50/30" />
      
      {/* Hero section with branding */}
      {!searchState.hasSearched && (
        <div className="relative z-10 pt-20 pb-32 text-center">
          <div className="animate-fade-in">
            <h1 className="text-5xl md:text-6xl font-light text-gray-900 mb-4 tracking-tight">
              AI 精選購物
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 mb-12 font-light">
              由人工智慧策劃的現代購物體驗
            </p>
          </div>
        </div>
      )}
      
      {/* Search Box */}
      <SearchBox
        onSearch={handleSearch}
        onReset={handleReset}
        isSearching={searchState.isSearching}
        hasSearched={searchState.hasSearched}
        query={searchState.query}
      />
      
      {/* Products Grid */}
      {searchState.hasSearched && (
        <div className="relative z-10 pt-24 pb-32">
          <div className="container mx-auto px-4">
            <div className="mb-8 text-center">
              <h2 className="text-2xl md:text-3xl font-light text-gray-900 mb-2">
                {searchState.query ? `「${searchState.query}」的搜尋結果` : '精選商品'}
              </h2>
              <p className="text-gray-600">
                找到 {displayProducts.length} 個符合的商品
              </p>
            </div>
            
            <ProductGrid 
              products={displayProducts} 
              isLoading={searchState.isSearching}
            />
          </div>
        </div>
      )}
      
      {/* Spacer for bottom search */}
      {searchState.hasSearched && <div className="h-24" />}
    </div>
  )
}