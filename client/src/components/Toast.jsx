import { useEffect, useState } from "react"
import "./Toast.css"

export const ToastTypes = {
  SUCCESS: "success",
  ERROR: "error",
  WARNING: "warning",
  INFO: "info",
}

const Toast = ({ id, message, type = ToastTypes.INFO, duration = 5000, onClose }) => {
  const [visible, setVisible] = useState(false)
  const [progress, setProgress] = useState(100)
  const [intervalId, setIntervalId] = useState(null)

  useEffect(() => {
    // Start entrance animation
    setTimeout(() => {
      setVisible(true)
    }, 10)

    // Set up progress bar
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev <= 0) {
          clearInterval(interval)
          handleClose()
          return 0
        }
        return prev - 100 / (duration / 100)
      })
    }, 100)

    setIntervalId(interval)

    // Auto-close after duration
    const timeout = setTimeout(() => {
      handleClose()
    }, duration)

    return () => {
      clearInterval(interval)
      clearTimeout(timeout)
    }
  }, [duration])

  const handleClose = () => {
    setVisible(false)
    clearInterval(intervalId)
    
    // Wait for exit animation to complete
    setTimeout(() => {
      onClose(id)
    }, 300)
  }

  const getIconByType = () => {
    switch (type) {
      case ToastTypes.SUCCESS:
        return (
          <div className="toast-icon success-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M22 11.08V12a10 10 0 1 1-5.93-9.14"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <polyline
                points="22 4 12 14.01 9 11.01"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        )
      case ToastTypes.ERROR:
        return (
          <div className="toast-icon error-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
              <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </div>
        )
      case ToastTypes.WARNING:
        return (
          <div className="toast-icon warning-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <line
                x1="12"
                y1="9"
                x2="12"
                y2="13"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <line
                x1="12"
                y1="17"
                x2="12.01"
                y2="17"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        )
      case ToastTypes.INFO:
      default:
        return (
          <div className="toast-icon info-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
              <line
                x1="12"
                y1="16"
                x2="12"
                y2="12"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <line
                x1="12"
                y1="8"
                x2="12.01"
                y2="8"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        )
    }
  }

  return (
    <div className={`toast ${type} ${visible ? "visible" : ""}`}>
      <div className="toast-content">
        {getIconByType()}
        <div className="toast-message">{message}</div>
        <button className="toast-close" onClick={handleClose}>
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
        </button>
      </div>
      <div className="toast-progress-container">
        <div className="toast-progress" style={{ width: `${progress}%` }}></div>
      </div>
      <div className="toast-glow"></div>
      <div className="toast-scanline"></div>
    </div>
  )
}

export default Toast
