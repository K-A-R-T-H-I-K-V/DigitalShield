import { useEffect, useState } from "react"
import "./ProgressRing.css"

const ProgressRing = ({
  progress = 0,
  size = 120,
  strokeWidth = 8,
  color = "#00f0ff",
  backgroundColor = "rgba(0, 240, 255, 0.1)",
  children,
}) => {
  const [offset, setOffset] = useState(0)

  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI

  useEffect(() => {
    const progressOffset = ((100 - progress) / 100) * circumference
    setOffset(progressOffset)
  }, [progress, circumference])

  return (
    <div className="progress-ring-container" style={{ width: size, height: size }}>
      <svg className="progress-ring" width={size} height={size}>
        <circle
          className="progress-ring-circle-bg"
          stroke={backgroundColor}
          strokeWidth={strokeWidth}
          fill="transparent"
          r={radius}
          cx={size / 2}
          cy={size / 2}
        />
        <circle
          className="progress-ring-circle"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={`${circumference} ${circumference}`}
          strokeDashoffset={offset}
          strokeLinecap="round"
          fill="transparent"
          r={radius}
          cx={size / 2}
          cy={size / 2}
        />
      </svg>
      <div className="progress-ring-content">{children}</div>
    </div>
  )
}

export default ProgressRing
