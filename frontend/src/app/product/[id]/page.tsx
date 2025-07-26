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
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-600 border-t-transparent"></div>
          <div className="animate-pulse text-gray-500 text-lg">載入中...</div>
        </div>
      </div>
    )
  }

  // Use the backend-provided color or default color
  const categoryColor = product.categoryColor || '#6B7280'

  // Generate AI Insight based on product category and title
  const generateAIInsight = (product: Product) => {
    const category = product.category.toLowerCase()
    const title = product.title.toLowerCase()
    
    if (category.includes('手機') || category.includes('電子')) {
      return `Based on your search for ${product.category} that combines cutting-edge technology with user-friendly design.`
    } else if (category.includes('配件') || category.includes('keyboard')) {
      return `Based on your search for professional ${product.category} that enhances productivity and comfort.`
    } else if (category.includes('耳機') || title.includes('headphone')) {
      return `Based on your search for premium audio equipment that delivers exceptional sound quality.`
    } else if (category.includes('健康') || title.includes('health')) {
      return `Based on your search for health monitoring devices that seamlessly integrate into your daily routine.`
    } else {
      return `Based on your search for ${product.category} that balances quality, functionality, and style.`
    }
  }

  const aiInsight = generateAIInsight(product)


  return (
    <>
      {/* 1. 頁首 Logo 導覽列（固定頂部） - 商品頁面反白樣式 */}
      <div className="fixed top-0 left-0 right-0 z-50 bg-gray-100 backdrop-blur-sm h-12 flex items-center px-6">
          <div className="text-xl font-medium tracking-wide text-purple">Reso</div>
      </div>

      {/* Main Content */}
      <div className="min-h-screen bg-gray-100 pt-12 flex items-center justify-center">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-4 sm:py-6 -mt-16">
          {/* 左右雙欄 Grid 排版 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8">
            
            {/* 2. 左欄：商品圖片 */}
            <div className="flex justify-center">
              <div className="w-full max-w-sm sm:max-w-md">
                <div className="bg-white rounded-2xl shadow-md overflow-hidden">
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
            <div className="space-y-6 max-w-lg">
              
              {/* 3. 右欄上半區：標題與 AI Insight */}
              <div className="space-y-4">
                {/* 標題區 - 使用商品分類作為主標題 */}
                <div className="flex items-center gap-3">
                  <div className="text-3xl">
                    {product.category.includes('手機') ? '📱' : 
                     product.category.includes('耳機') ? '🎧' : 
                     product.category.includes('配件') ? '⌨️' : 
                     product.category.includes('健康') ? '💍' : 
                     product.category.includes('筆電') ? '💻' : '🧥'}
                  </div>
                  <h1 className="text-2xl font-bold text-gray-900">{product.category}</h1>
                </div>
                
                {/* AI Insight 卡片 */}
                <div className="bg-white p-3 rounded-xl shadow-sm flex gap-2">
                  <span className="text-purple-500 text-lg">✨</span>
                  <p className="text-sm text-gray-600 leading-relaxed">
                    {aiInsight}
                  </p>
                </div>
              </div>

              {/* 4. 右欄中段：資訊卡片 + 價格 + 建議標籤 */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className={`grid gap-6 ${product.flowImage ? 'grid-cols-1 lg:grid-cols-2' : 'grid-cols-1'}`}>
                  
                  {/* 左側資訊卡 */}
                  <div className="space-y-3">
                    {/* 分類和品牌 badges */}
                    <div className="flex items-center justify-between">
                      <span 
                        className="text-xs font-medium px-2 py-1 rounded-full"
                        style={{
                          color: categoryColor,
                          backgroundColor: `${categoryColor}15`
                        }}
                      >
                        {product.category}
                      </span>
                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                        {product.brand || 'Keychron'}
                      </span>
                    </div>

                    {/* 商品名稱 - 使用實際商品標題 */}
                    <div className="space-y-1">
                      <h2 className="text-lg font-semibold text-gray-900">
                        {product.title}
                      </h2>
                      {/* 如果有副標題可以在這裡顯示 */}
                      <p className="text-sm text-gray-700">
                        {product.brand} 精選商品
                      </p>
                    </div>

                    {/* 價格 */}
                    <div className="text-right">
                      <div className="text-2xl font-bold text-blue-600">
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

              {/* 5. 右欄下半區：購買按鈕 */}
              <div className="space-y-3">
                <button 
                  className="w-full bg-green-500 text-white text-base font-semibold px-4 py-3 rounded-lg shadow-md hover:bg-green-600 transition-colors flex items-center justify-center gap-2"
                  onClick={() => window.open(product.url, '_blank')}
                >
                  購買商品
                </button>
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
