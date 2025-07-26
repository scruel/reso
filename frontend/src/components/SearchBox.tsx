'use client'

import { useState, useRef, useEffect } from 'react'
import { Search, X, Sparkles, ArrowUp } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SearchBoxProps {
  onSearch: (query: string) => void
  onReset: () => void
  isSearching: boolean
  hasSearched: boolean
  query: string
}

export function SearchBox({ onSearch, onReset, isSearching, hasSearched, query }: SearchBoxProps) {
  const [inputValue, setInputValue] = useState(query)
  const [isFocused, setIsFocused] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    setInputValue(query)
  }, [query])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputValue.trim()) {
      onSearch(inputValue.trim())
    }
  }

  const handleReset = () => {
    setInputValue('')
    onReset()
    inputRef.current?.focus()
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setInputValue(value)
    
    // Auto-search as user types (with debouncing handled in parent)
    if (hasSearched) {
      onSearch(value)
    }
  }

  return (
    <div className={cn(
      "transition-all duration-800 ease-out",
      hasSearched 
        ? "fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50 w-11/12 max-w-2xl"
        : "fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 w-11/12 max-w-2xl"
    )}>
      <form onSubmit={handleSubmit} className="relative group">
        {/* Search Input */}
        <div className="relative">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="Text whatever you want"
            className={cn(
              "w-full pl-8 pr-24 py-4",
              "bg-white/10 backdrop-blur-md",
              "border border-white/30",
              "rounded-[2rem]",
              "shadow-[inset_0_0_0.5px_rgba(255,255,255,0.5),0_4px_30px_rgba(0,0,0,0.1)]",
              "text-gray-900 placeholder-gray-500",
              "transition-all duration-300",
              isFocused && "scale-[1.015] outline-none ring-0"
            )}                                                                   
            disabled={isSearching}
          />
          
          {/* Search Icon
          <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400">
            {isSearching ? (
              <div className="animate-spin">
                <Sparkles className="w-5 h-5" />
              </div>
            ) : (
              <Search className="w-5 h-5" />
            )}
          </div> */}
          
          {/* Clear/Reset Button */}
          {(inputValue || hasSearched) && (
            <button
              type="button"
              onClick={handleReset}
              className="absolute right-16 top-1/2 transform -translate-y-1/2 p-1 rounded-full hover:bg-gray-100 transition-colors"
              title="清除"
            >
              <X className="w-4 h-4 text-gray-400" />
            </button>
          )}
          
          {/* Search Button */}
          {/* <button
            type="submit"
            disabled={isSearching || !inputValue.trim()}
            className={cn(
              "search-button",
              (!inputValue.trim() || isSearching) && "opacity-50 cursor-not-allowed"
            )}
            title="搜尋"
          >
            <Search className="w-5 h-5" />
          </button> */}
          <button
            type="submit"
            disabled={isSearching && !query.trim()}
            className={cn(
              "absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10",
              "rounded-full bg-black/30 backdrop-blur-sm",
              "flex items-center justify-center text-white",
              "hover:bg-black/40 transition-all duration-200"
            )}
          >
            {isSearching ? (
              <X className="w-5 h-5" />
            ) : query.trim() ? (
              <ArrowUp className="w-5 h-5" />
            ) : (
              <Search className="w-5 h-5" />
            )}
          </button>


        </div>
        
        {/* Search suggestions/hints */}
        {!hasSearched && (
          <div className="mt-6 text-center animate-fade-in">
            <div className="flex flex-wrap justify-center gap-2 text-sm">
              {[
                'iPhone', 
                'MacBook', 
                '筆電', 
                '耳機', 
                '智慧手錶', 
                '相機'
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => {
                    setInputValue(suggestion)
                    onSearch(suggestion)
                  }}
                  className="px-3 py-1.5 bg-white/60 backdrop-blur-sm text-gray-600 rounded-full hover:bg-white/80 hover:text-gray-900 transition-all duration-200 border border-gray-200/50"
                >
                  {suggestion}
                </button>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-4">
              或試試搜尋“智慧家居”、“遊戲主機”、“咖啡機”
            </p>
          </div>
        )}
      </form>
      
      {/* Loading state */}
      {isSearching && hasSearched && (
        <div className="mt-3 text-center">
          <div className="inline-flex items-center space-x-2 text-sm text-gray-600">
            <div className="animate-spin">
              <Sparkles className="w-4 h-4" />
            </div>
            <span>正在搜尋中...</span>
          </div>
        </div>
      )}
    </div>
  )
}