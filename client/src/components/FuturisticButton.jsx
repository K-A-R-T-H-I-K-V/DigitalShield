import { useState } from "react"
import "./FuturisticButton.css"

const FuturisticButton = ({
  children,
  onClick,
  type = "button",
  color = "primary",
  size = "medium",
  disabled = false,
  className = "",
}) => {
  const [isPressed, setIsPressed] = useState(false)

  const handleMouseDown = () => {
    if (!disabled) {
      setIsPressed(true)
    }
  }

  const handleMouseUp = () => {
    if (!disabled) {
      setIsPressed(false)
    }
  }

  const handleClick = (e) => {
    if (!disabled && onClick) {
      onClick(e)
    }
  }

  return (
    <button
      type={type}
      className={`futuristic-button ${color} ${size} ${isPressed ? "pressed" : ""} ${disabled ? "disabled" : ""} ${className}`}
      onClick={handleClick}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      disabled={disabled}
    >
      <div className="button-background"></div>
      <div className="button-glow"></div>
      <div className="button-content">{children}</div>
      <div className="button-border"></div>
    </button>
  )
}

export default FuturisticButton
