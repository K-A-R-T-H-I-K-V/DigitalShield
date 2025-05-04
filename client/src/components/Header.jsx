import { useState, useEffect } from "react"
import { Link } from "react-router-dom"
import "./Header.css"

const Header = ({ toggleSidebar }) => {
  const [currentTime, setCurrentTime] = useState(new Date())
  const [animatedText, setAnimatedText] = useState("")
  const fullText = "DATASHIELD"

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    let currentIndex = 0
    const textInterval = setInterval(() => {
      if (currentIndex <= fullText.length) {
        setAnimatedText(fullText.substring(0, currentIndex))
        currentIndex++
      } else {
        clearInterval(textInterval)
      }
    }, 150)

    return () => clearInterval(textInterval)
  }, [])

  const formattedTime = currentTime.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  })

  const formattedDate = currentTime.toLocaleDateString([], {
    year: "numeric",
    month: "short",
    day: "numeric",
  })

  return (
    <header className="header">
      <div className="header-left">
        <button className="menu-button" onClick={toggleSidebar}>
          <div className="menu-icon">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </button>
        <Link to="/" className="logo-container">
          <div className="logo">
            <span className="logo-text">{animatedText}</span>
            <div className="logo-underline"></div>
          </div>
        </Link>
      </div>

      <div className="header-right">
        <div className="datetime-display">
          <div className="time">{formattedTime}</div>
          <div className="date">{formattedDate}</div>
        </div>
        <div className="user-profile">
          <div className="user-avatar">
            <div className="avatar-hologram"></div>
          </div>
          <div className="user-info">
            <span className="user-name">SYSTEM ADMIN</span>
            <span className="user-status">AUTHORIZED</span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
