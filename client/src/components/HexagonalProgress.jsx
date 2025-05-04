import { useEffect, useState } from "react"
import "./HexagonalProgress.css"

const HexagonalProgress = ({
  progress = 0,
  size = 100,
  color = "#00f0ff",
  pulseColor = "rgba(0, 240, 255, 0.5)",
  label = "",
  value = "",
}) => {
  const [dashOffset, setDashOffset] = useState(0)

  // Calculate hexagon points
  const calculatePoints = () => {
    const hexRadius = size / 2
    const points = []

    for (let i = 0; i < 6; i++) {
      const angle = (Math.PI / 3) * i
      const x = hexRadius + hexRadius * Math.cos(angle)
      const y = hexRadius + hexRadius * Math.sin(angle)
      points.push(`${x},${y}`)
    }

    return points.join(" ")
  }
  const calculatePerimeter = () => {
    const sideLength = size * Math.sin(Math.PI / 3)
    return sideLength * 6
  }

  useEffect(() => {
    const perimeter = calculatePerimeter()
    const offset = ((100 - progress) / 100) * perimeter
    setDashOffset(offset)
  }, [progress, size])

  return (
    <div className="hexagonal-progress" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <polygon
          className="hexagon-bg"
          points={calculatePoints()}
          fill="rgba(0, 0, 0, 0.2)"
          stroke="rgba(255, 255, 255, 0.1)"
          strokeWidth="1"
        />
        <polygon
          className="hexagon-progress"
          points={calculatePoints()}
          fill="none"
          stroke={color}
          strokeWidth="2"
          strokeDasharray={calculatePerimeter()}
          strokeDashoffset={dashOffset}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <circle className="hexagon-pulse" cx={size / 2} cy={size / 2} r={size / 4} fill="none" stroke={pulseColor} />
      </svg>
      <div className="hexagon-content">
        {value && <div className="hexagon-value">{value}</div>}
        {label && <div className="hexagon-label">{label}</div>}
      </div>
    </div>
  )
}

export default HexagonalProgress
