'use client'

import React, { Component, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    this.setState({ error, errorInfo });
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      // 如果提供了自定义的 fallback，使用它
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // 否则显示默认的错误页面
      return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center">
          {/* Header */}
          <div className="fixed top-0 left-0 right-0 z-50 bg-gray-100 backdrop-blur-sm h-12 flex items-center px-6">
            <div className="text-xl font-medium tracking-wide text-sky-600">Reso</div>
          </div>

          <div className="max-w-2xl mx-auto px-4 py-8 mt-12">
            <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
              {/* Error Icon */}
              <div className="mb-6">
                <div className="w-16 h-16 mx-auto bg-orange-100 rounded-full flex items-center justify-center">
                  <AlertTriangle className="w-8 h-8 text-orange-500" />
                </div>
              </div>

              {/* Error Title and Message */}
              <h1 className="text-2xl font-bold text-gray-900 mb-3">應用程式發生錯誤</h1>
              <p className="text-gray-600 mb-6">
                很抱歉，應用程式遇到了一個意外錯誤。我們已經記錄了這個問題。
              </p>

              {/* Error Details (in development mode) */}
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <div className="mb-6 p-4 bg-gray-50 rounded-lg text-left">
                  <h3 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                    <Bug className="w-4 h-4" />
                    錯誤詳情 (開發模式)
                  </h3>
                  <pre className="text-xs text-red-600 overflow-auto max-h-32">
                    {this.state.error.message}
                    {this.state.error.stack}
                  </pre>
                </div>
              )}

              {/* Suggestions */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-3">建議操作：</h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-gray-400 rounded-full flex-shrink-0" />
                    重新載入頁面
                  </li>
                  <li className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-gray-400 rounded-full flex-shrink-0" />
                    返回首頁重新開始
                  </li>
                  <li className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-gray-400 rounded-full flex-shrink-0" />
                    如果問題持續發生，請聯繫技術支援
                  </li>
                </ul>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <button
                  onClick={this.handleReload}
                  className="px-6 py-2.5 bg-sky-500 text-white rounded-lg hover:bg-sky-600 transition-colors font-medium flex items-center justify-center gap-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  重新載入
                </button>

                <button
                  onClick={this.handleGoHome}
                  className="px-6 py-2.5 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors font-medium flex items-center justify-center gap-2"
                >
                  <Home className="w-4 h-4" />
                  返回首頁
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
