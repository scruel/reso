'use client'

import { useState, useEffect } from 'react'
import { X, CheckCircle, AlertCircle, XCircle, Info } from 'lucide-react'

export interface StatusMessageProps {
  status: number
  message: string
  show: boolean
  onClose: () => void
  autoClose?: boolean
  duration?: number
}

export default function StatusMessage({ 
  status, 
  message, 
  show, 
  onClose, 
  autoClose = true, 
  duration = 5000 
}: StatusMessageProps) {
  const [isVisible, setIsVisible] = useState(show)

  useEffect(() => {
    setIsVisible(show)
    
    if (show && autoClose) {
      const timer = setTimeout(() => {
        handleClose()
      }, duration)
      
      return () => clearTimeout(timer)
    }
  }, [show, autoClose, duration])

  const handleClose = () => {
    setIsVisible(false)
    setTimeout(() => {
      onClose()
    }, 300) // 等待动画完成
  }

  const getStatusConfig = () => {
    if (status >= 200 && status < 300) {
      return {
        icon: CheckCircle,
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200',
        iconColor: 'text-green-500',
        titleColor: 'text-green-800',
        textColor: 'text-green-700'
      }
    } else if (status >= 400 && status < 500) {
      return {
        icon: AlertCircle,
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-200',
        iconColor: 'text-yellow-500',
        titleColor: 'text-yellow-800',
        textColor: 'text-yellow-700'
      }
    } else if (status >= 500) {
      return {
        icon: XCircle,
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200',
        iconColor: 'text-red-500',
        titleColor: 'text-red-800',
        textColor: 'text-red-700'
      }
    } else {
      return {
        icon: Info,
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200',
        iconColor: 'text-blue-500',
        titleColor: 'text-blue-800',
        textColor: 'text-blue-700'
      }
    }
  }

  const getStatusTitle = () => {
    if (status >= 200 && status < 300) return '成功'
    if (status >= 400 && status < 500) return '客户端错误'
    if (status >= 500) return '服务器错误'
    return '信息'
  }

  if (!show) return null

  const config = getStatusConfig()
  const Icon = config.icon

  return (
    <div className="fixed inset-0 z-[9999] flex items-start justify-center pt-20 px-4">
      {/* 背景遮罩 */}
      <div 
        className={`fixed inset-0 bg-black transition-opacity duration-300 ${
          isVisible ? 'bg-opacity-20' : 'bg-opacity-0'
        }`}
        onClick={handleClose}
      />
      
      {/* 状态消息卡片 */}
      <div className={`
        relative bg-white rounded-lg shadow-lg border-2 p-6 max-w-md w-full
        transform transition-all duration-300 ease-out
        ${config.bgColor} ${config.borderColor}
        ${isVisible 
          ? 'translate-y-0 opacity-100 scale-100' 
          : '-translate-y-4 opacity-0 scale-95'
        }
      `}>
        {/* 关闭按钮 */}
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 p-1 rounded-full hover:bg-gray-100 transition-colors"
        >
          <X className="w-4 h-4 text-gray-400" />
        </button>

        {/* 内容 */}
        <div className="flex items-start space-x-3">
          <Icon className={`w-6 h-6 mt-0.5 ${config.iconColor}`} />
          
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <h3 className={`font-medium ${config.titleColor}`}>
                {getStatusTitle()}
              </h3>
              <span className={`text-sm px-2 py-0.5 rounded-full bg-gray-100 ${config.textColor}`}>
                {status}
              </span>
            </div>
            
            <p className={`text-sm ${config.textColor} leading-relaxed`}>
              {message}
            </p>
          </div>
        </div>

        {/* 进度条（自动关闭时显示） */}
        {autoClose && (
          <div className="mt-4 w-full bg-gray-200 rounded-full h-1">
            <div 
              className={`h-1 rounded-full transition-all ease-linear ${
                status >= 200 && status < 300 ? 'bg-green-500' :
                status >= 400 && status < 500 ? 'bg-yellow-500' :
                status >= 500 ? 'bg-red-500' : 'bg-blue-500'
              }`}
              style={{
                width: '100%',
                animation: `shrink ${duration}ms linear`
              }}
            />
          </div>
        )}
      </div>

      {/* CSS 动画 */}
      <style jsx>{`
        @keyframes shrink {
          from { width: 100%; }
          to { width: 0%; }
        }
      `}</style>
    </div>
  )
}
