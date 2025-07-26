import React from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Home, AlertCircle, Wifi, Server } from 'lucide-react';

interface ErrorInfo {
  type: string;
  title: string;
  message: string;
  icon: React.ComponentType<{ className?: string }>;
  suggestions: string[];
}

function getGeneralErrorInfo(error: any): ErrorInfo {
  if (!error) return {
    type: 'unknown',
    title: '未知錯誤',
    message: '發生了一個未知錯誤。',
    icon: AlertCircle,
    suggestions: [
      '刷新頁面重試',
      '檢查網絡連接',
      '返回首頁'  
    ]
  };

  const errorMessage = error.message?.toLowerCase() || '';

  if (errorMessage.includes('network') || errorMessage.includes('connect')) {
    return {
      type: 'network_error',
      title: '網絡連接錯誤',
      message: '無法連接到服務器，請檢查您的網絡連接。',
      icon: Wifi,
      suggestions: [
        '檢查網絡連接是否正常',
        '刷新頁面重試',
        '稍後再試'
      ]
    };
  }

  if (errorMessage.includes('500') || errorMessage.includes('server')) {
    return {
      type: 'server_error',
      title: '服務器錯誤',
      message: '服務器暫時無法處理請求。',
      icon: Server,
      suggestions: [
        '稍後再試',
        '刷新頁面重試',
        '聯繫客服支援'
      ]
    };
  }

  if (errorMessage.includes('404') || errorMessage.includes('not found')) {
    return {
      type: 'not_found',
      title: '資源不存在',
      message: '我們找不到您要查找的頁面。',
      icon: AlertCircle,
      suggestions: [
        '返回首頁',
        '嘗試其他頁面'
      ]
    };
  }

  return {
    type: 'unknown',
    title: '未知錯誤',
    message: '發生了一個未知錯誤。',
    icon: AlertCircle,
    suggestions: [
      '刷新頁面重試',
      '檢查網絡連接',
      '返回首頁'
    ]
  };
}

export default function ErrorPage({ error }: { error: any }) {
  const router = useRouter();
  const errorInfo = getGeneralErrorInfo(error);
  const IconComponent = errorInfo.icon;

  return (
    <>
      <div className="fixed top-0 left-0 right-0 z-50 bg-gray-100 backdrop-blur-sm h-12 flex items-center px-6">
        <div className="text-xl font-medium tracking-wide text-sky-600">Reso</div>
      </div>

      <div className="min-h-screen bg-gray-100 pt-12 flex items-center justify-center">
        <div className="max-w-2xl mx-auto px-4 py-8">
          <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
            <div className="mb-6">
              <div className="w-16 h-16 mx-auto bg-red-100 rounded-full flex items-center justify-center">
                <IconComponent className="w-8 h-8 text-red-500" />
              </div>
            </div>

            <h1 className="text-2xl font-bold text-gray-900 mb-3">{errorInfo.title}</h1>
            <p className="text-gray-600 mb-6">{errorInfo.message}</p>

            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-700 mb-3">建議操作：</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                {errorInfo.suggestions.map((suggestion, index) => (
                  <li key={index} className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-gray-400 rounded-full flex-shrink-0" />
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>

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
                className="px-6 py-2.5 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors font-medium flex items-center justify-center gap-2"
              >
                <Home className="w-4 h-4" />
                返回首頁
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

