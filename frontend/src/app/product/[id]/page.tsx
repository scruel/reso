'use client'

import { useState, useEffect } from 'react'
import { notFound } from 'next/navigation'
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

  // AI Insight message
  const aiInsight = "Based on your search for work attire that balances packability with professional style."

  // Recommendation tags
  const recommendationTags = [
    'Top 8 brands for blazers',
    'Brook\'s Brother',
    'Ralph Lauren men blazer',
    'what you\'ll need for absolute comfort in business trip'
  ]

  return (
    <>
      {/* 1. 頁首 Logo 導覽列（固定頂部） */}
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
          {/* 左右雙欄 Grid 排版 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            
            {/* 2. 左欄：商品圖片 */}
            <div className="flex justify-center">
              <div className="w-full max-w-lg">
                <div className="bg-white rounded-3xl shadow-lg overflow-hidden">
                  <div className="aspect-square relative">
                    {/* 漸層 loading 效果 */}
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

            {/* 右欄：文字資訊與互動區塊 */}
            <div className="space-y-8">
              
              {/* 3. 右欄上半區：標題與 AI Insight */}
              <div className="space-y-6">
                {/* 標題區 */}
                <div className="flex items-center gap-4">
                  <div className="text-5xl">🧥</div>
                  <h1 className="text-4xl font-bold text-gray-900">Blazer</h1>
                </div>
                
                {/* AI Insight 卡片 */}
                <div className="bg-white p-4 rounded-2xl shadow-sm flex gap-2">
                  <span className="text-purple-500 text-xl">✨</span>
                  <p className="text-lg text-gray-600 leading-relaxed">
                    {aiInsight}
                  </p>
                </div>
              </div>

              {/* 4. 右欄中段：資訊卡片 + 價格 + 建議標籤 */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  
                  {/* 左側資訊卡 */}
                  <div className="space-y-4">
                    {/* 分類和品牌 badges */}
                    <div className="flex items-center justify-between">
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
                        {product.brand || 'Keychron'}
                      </span>
                    </div>

                    {/* 商品名稱 */}
                    <div className="space-y-1">
                      <h2 className="text-xl font-semibold text-gray-900">
                        Blue navy light jacket
                      </h2>
                      <p className="text-lg text-gray-700">
                        light jacket
                      </p>
                      {/* 原始商品名稱作為參考 */}
                      <p className="text-sm text-gray-500 line-through">
                        {product.title}
                      </p>
                    </div>

                    {/* 價格 */}
                    <div className="text-right">
                      <div className="text-3xl font-bold text-blue-600">
                        {formatPrice(product.price)}
                      </div>
                    </div>
                  </div>

                  {/* 右側流程圖 */}
                  {product.flowImage && (
                    <div className="relative">
                      <div className="rounded-xl overflow-hidden relative">
                        <img
                          src={product.flowImage}
                          alt={`${product.title} 使用流程`}
                          className="w-full h-auto object-cover"
                        />
                        {/* 作者資訊 badge */}
                        <div className="absolute bottom-2 right-2 flex items-center gap-2 bg-white/90 backdrop-blur-sm rounded-full px-3 py-1 shadow-sm">
                          <div className="w-5 h-5 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white text-xs font-medium">
                            {product.author ? product.author.charAt(0).toUpperCase() : 'A'}
                          </div>
                          <span className="text-xs font-medium text-gray-700">
                            {product.author || 'Alex'}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* 5. 右欄下半區：推薦標籤區（Tag Buttons） */}
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-gray-900">延伸搜尋建議</h3>
                <div className="flex flex-wrap gap-2">
                  {recommendationTags.map((tag, index) => (
                    <Link
                      key={index}
                      href={`/?q=${encodeURIComponent(tag)}`}
                      className="inline-block bg-blue-600 text-white text-sm px-4 py-2 rounded-full hover:bg-blue-700 transition-colors"
                    >
                      {tag}
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom fade overlay for dreamy effect */}
        <div className="fixed bottom-0 left-0 right-0 h-24 pointer-events-none z-30 bg-gradient-to-t from-gray-100 via-gray-100/60 to-transparent" />
      </div>
    </>
  )
}
