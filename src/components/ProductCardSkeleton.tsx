'use client'

interface ProductCardSkeletonProps {
  delay?: number
}

export function ProductCardSkeleton({ delay = 0 }: ProductCardSkeletonProps) {
  return (
    <div 
      className="product-card animate-pulse"
      style={{ animationDelay: `${delay}ms` }}
    >
      {/* Image skeleton */}
      <div className="aspect-square rounded-t-2xl bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 bg-[length:200%_100%] animate-pulse" />
      
      {/* Content skeleton */}
      <div className="p-4 space-y-3">
        {/* Category & Brand */}
        <div className="flex items-center justify-between">
          <div className="h-5 w-16 bg-gray-200 rounded-md" />
          <div className="h-4 w-12 bg-gray-200 rounded" />
        </div>
        
        {/* Title */}
        <div className="space-y-2">
          <div className="h-4 w-full bg-gray-200 rounded" />
          <div className="h-4 w-3/4 bg-gray-200 rounded" />
        </div>
        
        {/* Price */}
        <div className="h-6 w-20 bg-gray-200 rounded" />
        
        {/* Button */}
        <div className="h-10 w-full bg-gray-200 rounded-xl" />
      </div>
    </div>
  )
}