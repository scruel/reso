'use client'

import { useState, useEffect } from 'react'
import { notFound, useRouter } from 'next/navigation'
import Image from 'next/image'
import { ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import { mockProducts } from '@/data/products'
import { Product } from '@/types/product'
import { formatPrice } from '@/lib/utils'

interface ProductDetailPageProps {
  params: Promise<{ id: string }>
}

export default function ProductDetailPage({ params }: ProductDetailPageProps) {
  const [product, setProduct] = useState<Product | null>(null)
  const [isImageLoaded, setIsImageLoaded] = useState(false)
  const [productId, setProductId] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    // Handle async params
    const getParams = async () => {
      const resolvedParams = await params
      setProductId(resolvedParams.id)
      
      // Find product by ID from mock data
      const foundProduct = mockProducts.find(p => p.id === resolvedParams.id)
      if (foundProduct) {
        setProduct(foundProduct)
      } else {
        notFound()
      }
    }
    
    getParams()
  }, [params])

  if (!product) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="animate-pulse text-gray-500">載入中...</div>
      </div>
    )
  }

  // Use the backend-provided color or default color
  const categoryColor = product.categoryColor || '#6B7280'

  return (
    <>
      {/* Purple Top Navigation Bar */}
      <div className="fixed top-0 left-0 right-0 z-50 bg-purple-600 h-12 flex items-center px-6">
        <Link 
          href="/" 
          className="flex items-center gap-3 text-white hover:text-purple-200 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          <div className="text-xl font-medium tracking-wide">Reso</div>
        </Link>
      </div>

      {/* Main Content */}
      <div className="min-h-screen bg-gray-100 pt-12">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            
            {/* Left Side - Product Image */}
            <div className="flex justify-center">
              <div className="w-full max-w-lg">
                <div className="bg-white rounded-3xl shadow-lg overflow-hidden">
                  <div className="aspect-square relative">
                    {!isImageLoaded && (
                      <div className="absolute inset-0 bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 animate-pulse" />
                    )}
                    <Image
                      src={product.image}
                      alt={product.title}
                      fill
                      className={`object-cover transition-opacity duration-500 ${
                        isImageLoaded ? 'opacity-100' : 'opacity-0'
                      }`}
                      onLoad={() => setIsImageLoaded(true)}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Right Side - Product Information */}
            <div className="space-y-8">
              
              {/* Product Title Section */}
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <div className="text-5xl">🧥</div>
                  <h1 className="text-4xl font-bold text-gray-900">Blazer</h1>
                  <div className="text-2xl">✨</div>
                </div>
                
                <p className="text-lg text-gray-600 leading-relaxed">
                  Based on your search for work attire that balances packability with professional style.
                </p>
              </div>

              {/* Category Badge */}
              <div className="flex items-center gap-4">
                <span 
                  className="text-sm font-medium px-3 py-1.5 rounded-full"
                  style={{
                    color: categoryColor,
                    backgroundColor: `${categoryColor}15`
                  }}
                >
                  {product.category}
                </span>
                <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1.5 rounded-full">
                  Keychron
                </span>
              </div>

              {/* Product Name and Price */}
              <div className="space-y-2">
                <h2 className="text-2xl font-semibold text-gray-900">
                  {product.title}
                </h2>
                <div className="text-3xl font-bold text-blue-600">
                  {formatPrice(product.price)}
                </div>
              </div>

              {/* Tags/Attributes */}
              <div className="space-y-3">
                <div className="flex flex-wrap gap-2">
                  {[
                    'Top 8 brands for blazers',
                    'Brook\'s Brother',
                    'Ralph Lauren men blazer',
                    'what you\'ll need for absolute comfort in business trip'
                  ].map((tag, index) => (
                    <Link
                      key={index}
                      href="#"
                      className="text-sm text-blue-600 hover:text-blue-800 underline transition-colors"
                    >
                      {tag}
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Flow Image Section */}
          {product.flowImage && (
            <div className="mt-16">
              <div className="bg-white rounded-3xl shadow-lg overflow-hidden relative">
                <img
                  src={product.flowImage}
                  alt={`${product.title} 使用流程`}
                  className="w-full h-auto"
                />
                {/* Author overlay */}
                <div className="absolute bottom-4 right-4 flex items-center gap-2 bg-white/90 backdrop-blur-sm rounded-full px-3 py-2 shadow-sm">
                  <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white text-xs font-medium">
                    {product.author ? product.author.charAt(0).toUpperCase() : 'A'}
                  </div>
                  <span className="text-sm font-medium text-gray-700">
                    {product.author || 'Anonymous'}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Bottom fade overlay for dreamy effect */}
        <div className="fixed bottom-0 left-0 right-0 h-24 pointer-events-none z-30 bg-gradient-to-t from-gray-100 via-gray-100/60 to-transparent" />
      </div>
    </>
  )
}
