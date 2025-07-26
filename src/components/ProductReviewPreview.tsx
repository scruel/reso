'use client'

import { useState } from 'react'
import { Product } from '@/types/product'
import Image from 'next/image'

interface Props {
  product: Product
}

export function ProductReviewPreview({ product }: Props) {
  const [expanded, setExpanded] = useState(false)
  if (!product.review) return null

  const { title, paragraphs, userName = 'Alex', avatar = '/avatar.png' } = product.review
  const previewText = expanded
    ? paragraphs.join('\n')
    : paragraphs[0].slice(0, 60) + (paragraphs[0].length > 60 ? '…' : '')

  return (
    <div className="relative mt-0">
      {/* 連接線 + 節點 */}
      <div className="flex justify-center -mt-1 pointer-events-none">
        <div className="w-0.5 h-3 bg-orange-400" />
        <div className="w-2.5 h-2.5 bg-orange-400 rounded-full -ml-[5px]" />
      </div>

      {/* Review 卡片（縮圖 + 用戶） */}
      <div
        className="mt-2 flex items-start space-x-3 bg-white rounded-2xl shadow-sm p-3 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        {/* 左側縮圖 */}
        <div className="flex-shrink-0 w-14 h-14 rounded-xl overflow-hidden">
          <Image
            src={product.image}
            alt={product.title}
            width={56}
            height={56}
            className="object-cover w-full h-full"
          />
        </div>

        {/* 右側文字 */}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-orange-500 mb-1">🧡 {title}</p>
          <p className="text-xs text-gray-700 leading-snug whitespace-pre-wrap">
            {previewText}
          </p>
          <div className="mt-1 flex items-center space-x-1.5">
            <Image
              src={avatar}
              alt={userName}
              width={16}
              height={16}
              className="rounded-full"
            />
            <span className="text-xs text-gray-500">{userName}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
