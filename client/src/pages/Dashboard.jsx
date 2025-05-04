import { useState, useEffect } from "react"
import { Link } from "react-router-dom"
import HolographicCard from "../components/HolographicCard"
import ProgressRing from "../components/ProgressRing"
import HexagonalProgress from "../components/HexagonalProgress"
import FuturisticButton from "../components/FuturisticButton"
import { showToast, ToastTypes } from "../components/ToastContainer"
import "./Dashboard.css"

const Dashboard = () => {
  const [stats, setStats] = useState({
    imagesProtected: 0,
    activeTracking: 0,
    revocationRate: 0,
  })

  const [isLoading, setIsLoading] = useState(true)
  const [systemHealth, setSystemHealth] = useState({
    blockchain: { status: "CONNECTING", progress: 0 },
    ipfs: { status: "CONNECTING", progress: 0 },
    encryption: { status: "INITIALIZING", progress: 0 },
    aiDefense: { status: "LOADING", progress: 0 },
  })

  const [networkActivity, setNetworkActivity] = useState([])

  useEffect(() => {
    // Simulate loading data
    showToast("Loading system metrics...", ToastTypes.INFO)

    // Simulate progressive loading of system health
    const healthInterval = setInterval(() => {
      setSystemHealth((prev) => {
        const newHealth = { ...prev }

        if (newHealth.blockchain.progress < 92) {
          newHealth.blockchain.progress += 5
          if (newHealth.blockchain.progress >= 50) newHealth.blockchain.status = "SYNCING"
          if (newHealth.blockchain.progress >= 92) newHealth.blockchain.status = "ONLINE"
        }

        if (newHealth.ipfs.progress < 88) {
          newHealth.ipfs.progress += 6
          if (newHealth.ipfs.progress >= 50) newHealth.ipfs.status = "CONNECTING"
          if (newHealth.ipfs.progress >= 88) newHealth.ipfs.status = "CONNECTED"
        }

        if (newHealth.encryption.progress < 95) {
          newHealth.encryption.progress += 7
          if (newHealth.encryption.progress >= 50) newHealth.encryption.status = "VERIFYING"
          if (newHealth.encryption.progress >= 95) newHealth.encryption.status = "ACTIVE"
        }

        if (newHealth.aiDefense.progress < 90) {
          newHealth.aiDefense.progress += 8
          if (newHealth.aiDefense.progress >= 50) newHealth.aiDefense.status = "CALIBRATING"
          if (newHealth.aiDefense.progress >= 90) newHealth.aiDefense.status = "ENABLED"
        }

        return newHealth
      })
    }, 200)

    // Generate fake network activity logs
    const activityInterval = setInterval(() => {
      if (networkActivity.length < 5) {
        const activities = [
          { type: "blockchain", message: "Block #3928472 verified", timestamp: new Date() },
          { type: "ipfs", message: "Content pinned: QmX72...", timestamp: new Date() },
          { type: "encryption", message: "New key generated", timestamp: new Date() },
          { type: "aiDefense", message: "Pattern analysis complete", timestamp: new Date() },
          { type: "system", message: "System scan completed", timestamp: new Date() },
        ]

        const randomActivity = activities[Math.floor(Math.random() * activities.length)]
        setNetworkActivity((prev) => [...prev, randomActivity])
      }
    }, 800)

    const timer = setTimeout(() => {
      setStats({
        imagesProtected: 128,
        activeTracking: 96,
        revocationRate: 78,
      })
      setIsLoading(false)
      showToast("System metrics loaded successfully", ToastTypes.SUCCESS)

      clearInterval(healthInterval)
      clearInterval(activityInterval)
    }, 3000)

    return () => {
      clearTimeout(timer)
      clearInterval(healthInterval)
      clearInterval(activityInterval)
    }
  }, [networkActivity.length])

  const phases = [
    {
      id: "poison",
      title: "PHASE 1: POISONING",
      description:
        "Embed imperceptible noise patterns that disrupt AI models when they attempt to train on your images.",
      icon: "poison-icon",
      color: "#00f0ff",
      path: "/poison",
    },
    {
      id: "track",
      title: "PHASE 2: TRACKING",
      description:
        "Invisibly watermark and pin your images to IPFS with blockchain verification for traceable ownership.",
      icon: "track-icon",
      color: "#ff00e6",
      path: "/track",
    },
    {
      id: "revoke",
      title: "PHASE 3: REVOKING",
      description: "Unpin images from IPFS and delete encryption keys from the blockchain to revoke access.",
      icon: "revoke-icon",
      color: "#00ff88",
      path: "/revoke",
    },
  ]

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="header-content">
          <h1 className="page-title">DATASHIELD COMMAND CENTER</h1>
          <p className="page-subtitle">
            Advanced Image Protection System <span className="version">v2.8.5</span>
          </p>
        </div>
        <div className="system-status-badge">
          <div className="status-indicator"></div>
          SYSTEM OPERATIONAL
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="stats-section">
          <HolographicCard title="SYSTEM METRICS" className="stats-card">
            <div className="stats-container">
              <div className="stat-item">
                <ProgressRing progress={isLoading ? 0 : 85} size={140} color="#00f0ff">
                  <div className="stat-value">{isLoading ? "..." : stats.imagesProtected}</div>
                  <div className="stat-label">PROTECTED</div>
                </ProgressRing>
              </div>

              <div className="stat-item">
                <ProgressRing progress={isLoading ? 0 : 75} size={140} color="#ff00e6">
                  <div className="stat-value">{isLoading ? "..." : stats.activeTracking}</div>
                  <div className="stat-label">TRACKING</div>
                </ProgressRing>
              </div>

              <div className="stat-item">
                <ProgressRing progress={isLoading ? 0 : stats.revocationRate} size={140} color="#00ff88">
                  <div className="stat-value">{isLoading ? "..." : `${stats.revocationRate}%`}</div>
                  <div className="stat-label">REVOKED</div>
                </ProgressRing>
              </div>
            </div>
          </HolographicCard>

          <HolographicCard title="SYSTEM STATUS" className="system-card" glowColor="#ff00e6">
            <div className="system-status-container">
              <div className="system-grid">
                <HexagonalProgress
                  progress={systemHealth.blockchain.progress}
                  label="BLOCKCHAIN"
                  value={systemHealth.blockchain.status}
                  color="#ff00e6"
                />
                <HexagonalProgress
                  progress={systemHealth.ipfs.progress}
                  label="IPFS"
                  value={systemHealth.ipfs.status}
                  color="#00ff88"
                />
                <HexagonalProgress
                  progress={systemHealth.encryption.progress}
                  label="ENCRYPTION"
                  value={systemHealth.encryption.status}
                  color="#00f0ff"
                />
                <HexagonalProgress
                  progress={systemHealth.aiDefense.progress}
                  label="AI DEFENSE"
                  value={systemHealth.aiDefense.status}
                  color="#ffae00"
                />
              </div>

              <div className="system-details">
                <div className="system-details-header">
                  <h3>NETWORK ACTIVITY</h3>
                  <div className="pulse-indicator"></div>
                </div>

                <div className="activity-log">
                  {networkActivity.length > 0 ? (
                    networkActivity.map((activity, index) => (
                      <div key={index} className={`activity-item ${activity.type}`}>
                        <div className="activity-time">
                          {activity.timestamp.toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                            second: "2-digit",
                          })}
                        </div>
                        <div className="activity-message">{activity.message}</div>
                      </div>
                    ))
                  ) : (
                    <div className="activity-placeholder">Initializing network monitoring...</div>
                  )}
                </div>

                <div className="system-metrics">
                  <div className="metric">
                    <div className="metric-label">CPU LOAD</div>
                    <div className="metric-bar">
                      <div className="metric-fill" style={{ width: "42%" }}></div>
                    </div>
                    <div className="metric-value">42%</div>
                  </div>
                  <div className="metric">
                    <div className="metric-label">MEMORY</div>
                    <div className="metric-bar">
                      <div className="metric-fill" style={{ width: "68%" }}></div>
                    </div>
                    <div className="metric-value">68%</div>
                  </div>
                  <div className="metric">
                    <div className="metric-label">NETWORK</div>
                    <div className="metric-bar">
                      <div className="metric-fill" style={{ width: "35%" }}></div>
                    </div>
                    <div className="metric-value">35%</div>
                  </div>
                </div>
              </div>
            </div>
          </HolographicCard>
        </div>

        <div className="phases-section">
          {phases.map((phase) => (
            <HolographicCard
              key={phase.id}
              title={phase.title}
              className={`phase-card ${phase.id}-card`}
              glowColor={phase.color}
            >
              <div className="phase-content">
                <div className="phase-header">
                  <div className={`phase-icon ${phase.icon}`}></div>
                  <div className="phase-status-indicator" style={{ backgroundColor: phase.color }}></div>
                </div>
                <p className="phase-description">{phase.description}</p>

                <Link to={phase.path} className="phase-button-container">
                  <FuturisticButton
                    color={phase.id}
                    onClick={() => {
                      showToast(`Navigating to ${phase.title}`, ToastTypes.INFO)
                    }}
                  >
                    ENTER {phase.id.toUpperCase()} MODULE
                  </FuturisticButton>
                </Link>
              </div>
            </HolographicCard>
          ))}
        </div>
      </div>

      <div className="dashboard-footer">
        <div className="footer-status">
          <div className="footer-status-item">
            <div className="status-dot green"></div>
            <span>API: ONLINE</span>
          </div>
          <div className="footer-status-item">
            <div className="status-dot green"></div>
            <span>DATABASE: CONNECTED</span>
          </div>
          <div className="footer-status-item">
            <div className="status-dot yellow"></div>
            <span>BLOCKCHAIN: SYNCING</span>
          </div>
        </div>
        <div className="footer-timestamp">LAST UPDATED: {new Date().toLocaleString()}</div>
      </div>
    </div>
  )
}

export default Dashboard
