import { useState, useEffect } from "react"
import "./HolographicCard.css"

const HolographicCard = ({ title, children, glowColor = "#00f0ff", className = "" }) => {
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [isHovered, setIsHovered] = useState(false)

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const x = ((e.clientX - rect.left) / rect.width) * 100
    const y = ((e.clientY - rect.top) / rect.height) * 100

    setPosition({ x, y })
  }

  const handleMouseEnter = () => {
    setIsHovered(true)
  }

  const handleMouseLeave = () => {
    setIsHovered(false)
    setPosition({ x: 50, y: 50 })
  }

  useEffect(() => {
    if (!isHovered) {
      const timeout = setTimeout(() => {
        setPosition({ x: 50, y: 50 })
      }, 500)

      return () => clearTimeout(timeout)
    }
  }, [isHovered])

  const cardStyle = {
    "--x": `${position.x}%`,
    "--y": `${position.y}%`,
    "--glow-color": glowColor,
  }

  return (
    <div
      className={`holographic-card ${className} ${isHovered ? "hovered" : ""}`}
      style={cardStyle}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div className="card-content">
        {title && <div className="card-title">{title}</div>}
        <div className="card-body">{children}</div>
      </div>
      <div className="card-glow"></div>
      <div className="card-reflection"></div>
      <div className="card-scanline"></div>
    </div>
  )
}

export default HolographicCard
