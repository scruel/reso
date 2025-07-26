import { useState, useCallback } from 'react'

interface StatusMessageState {
  status: number
  message: string
  show: boolean
}

export function useStatusMessage() {
  const [statusMessage, setStatusMessage] = useState<StatusMessageState>({
    status: 0,
    message: '',
    show: false
  })

  const showStatusMessage = useCallback((status: number, message: string) => {
    setStatusMessage({
      status,
      message,
      show: true
    })
  }, [])

  const hideStatusMessage = useCallback(() => {
    setStatusMessage(prev => ({
      ...prev,
      show: false
    }))
  }, [])

  // 便捷方法
  const showSuccess = useCallback((message: string) => {
    showStatusMessage(200, message)
  }, [showStatusMessage])

  const showError = useCallback((message: string, status: number = 500) => {
    showStatusMessage(status, message)
  }, [showStatusMessage])

  const showWarning = useCallback((message: string) => {
    showStatusMessage(400, message)
  }, [showStatusMessage])

  const showInfo = useCallback((message: string) => {
    showStatusMessage(0, message)
  }, [showStatusMessage])

  return {
    statusMessage,
    showStatusMessage,
    hideStatusMessage,
    showSuccess,
    showError,
    showWarning,
    showInfo
  }
}
