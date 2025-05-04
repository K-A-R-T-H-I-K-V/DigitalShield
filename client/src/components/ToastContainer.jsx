"use client"

import { useState, useEffect } from "react"
import "./ToastContainer.css"

export const ToastTypes = {
  SUCCESS: "success",
  ERROR: "error",
  INFO: "info",
  WARNING: "warning",
}

let toastIdCounter = 0

export const showToast = (message, type = ToastTypes.INFO, duration = 3000) => {
  const id = toastIdCounter++
  const event = new CustomEvent("showToast", {
    detail: {
      id,
      message,
      type,
      duration,
    },
  })
  document.dispatchEvent(event)
  return id
}

const ToastContainer = () => {
  const [toasts, setToasts] = useState([])

  useEffect(() => {
    const handleShowToast = (event) => {
      const { id, message, type, duration } = event.detail
      setToasts((prevToasts) => [...prevToasts, { id, message, type, duration }])
    }

    document.addEventListener("showToast", handleShowToast)

    return () => {
      document.removeEventListener("showToast", handleShowToast)
    }
  }, [])

  useEffect(() => {
    if (toasts.length > 0) {
      const timeoutId = setTimeout(() => {
        removeToast(toasts[0].id)
      }, toasts[0].duration)

      return () => clearTimeout(timeoutId)
    }
  }, [toasts])

  const removeToast = (id) => {
    setToasts((prevToasts) => prevToasts.filter((toast) => toast.id !== id))
  }

  return (
    <div className="toast-container">
      {toasts.map((toast) => (
        <div key={toast.id} className={`toast ${toast.type}`}>
          <div className="toast-icon"></div>
          <div className="toast-message">{toast.message}</div>
          <button className="toast-close-button" onClick={() => removeToast(toast.id)}>
            <div className="close-icon"></div>
          </button>
        </div>
      ))}
    </div>
  )
}

export default ToastContainer
