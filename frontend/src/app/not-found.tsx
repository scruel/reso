'use client'

import { useRouter } from 'next/navigation';
import { Home, ArrowLeft, Search, MapPin } from 'lucide-react';

export default function NotFound() {
  const router = useRouter();

  return (
    <>
      {/* Header */}
      <div className="fixed top-0 left-0 right-0 z-50 bg-gray-100 backdrop-blur-sm h-12 flex items-center px-6">
        <div className="text-xl font-medium tracking-wide text-sky-600">Reso</div>
      </div>

      <div className="min-h-screen bg-gray-100 pt-12 flex items-center justify-center">
        <div className="max-w-2xl mx-auto px-4 py-8">
          <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
            {/* 404 Icon */}
            <div className="mb-6">
              <div className="w-20 h-20 mx-auto bg-blue-100 rounded-full flex items-center justify-center">
                <MapPin className="w-10 h-10 text-blue-500" />
              </div>
            </div>

            {/* Large 404 Text */}
            <div className="mb-4">
              <h1 className="text-6xl font-bold text-gray-300 mb-2">404</h1>
              <h2 className="text-2xl font-bold text-gray-900 mb-3">頁面不存在</h2>
            </div>

            <p className="text-gray-600 mb-6">
              很抱歉，我們找不到您要查找的頁面。該頁面可能已被移動、刪除或從未存在過。
            </p>

            {/* Search suggestion */}
            <div className="bg-gray-50 rounded-xl p-4 mb-6">
              <h3 className="text-sm font-medium text-gray-700 mb-2 flex items-center justify-center gap-2">
                <Search className="w-4 h-4" />
                建議您可以嘗試：
              </h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full flex-shrink-0" />
                  檢查網址是否正確
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full flex-shrink-0" />
                  返回首頁開始瀏覽
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full flex-shrink-0" />
                  使用搜索功能查找商品
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full flex-shrink-0" />
                  瀏覽我們的精選商品
                </li>
              </ul>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button
                onClick={() => router.back()}
                className="px-6 py-2.5 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors font-medium flex items-center justify-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                返回上頁
              </button>

              <button
                onClick={() => router.push('/')}
                className="px-6 py-2.5 bg-sky-500 text-white rounded-lg hover:bg-sky-600 transition-colors font-medium flex items-center justify-center gap-2"
              >
                <Home className="w-4 h-4" />
                返回首頁
              </button>
            </div>

            {/* Additional help */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <p className="text-xs text-gray-500">
                如果您認為這是一個錯誤，或者需要幫助，請聯繫我們的客服團隊。
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
