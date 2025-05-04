"use client"

import { useState } from "react"
import axios from "axios"
import HolographicCard from "../components/HolographicCard"
import FuturisticButton from "../components/FuturisticButton"
import { showToast, ToastTypes } from "../components/ToastContainer"
import "./TrackPage.css"

const TrackPage = () => {
  const [trackingId, setTrackingId] = useState("")
  const [isMonitoring, setIsMonitoring] = useState(false)
  const [monitoringResults, setMonitoringResults] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  const handleTrackingIdChange = (e) => {
    setTrackingId(e.target.value)
  }

  const handleMonitorCid = async () => {
    if (!trackingId) return

    setIsMonitoring(true)
    setMonitoringResults(null)
    showToast(`Monitoring CID: ${trackingId}...`, ToastTypes.INFO)

    try {
      // Make API request using axios
      const response = await axios.post("http://localhost:5000/api/monitor", {
        cid: trackingId,
      })

      // Process successful response
      if (response.data) {
        setMonitoringResults({
          status: "success",
          results: response.data.results || [],
        })
        showToast(`Monitoring complete`, ToastTypes.SUCCESS)
      } else {
        throw new Error("No data received from server")
      }
    } catch (error) {
      console.error("Error monitoring CID:", error)
      setMonitoringResults({
        status: "error",
        message: "Failed to monitor CID",
        error: error.response?.data?.error || error.message,
      })
      showToast(`Monitoring failed: ${error.response?.data?.error || error.message}`, ToastTypes.ERROR)
    } finally {
      setIsMonitoring(false)
    }
  }

  return (
    <div className="track-page">
      <div className="page-header">
        <h1 className="page-title">PHASE 2: TRACKING</h1>
        <p className="page-subtitle">Monitor and track your protected images</p>
      </div>

      <div className="track-content">
        <HolographicCard title="MONITORING CONSOLE" className="monitor-card" glowColor="#ff00e6">
          <div className="monitor-content">
            <div className="monitor-form">
              <div className="input-group">
                <label htmlFor="tracking-id" className="input-label">
                  CID TO MONITOR
                </label>
                <div className="input-container">
                  <input
                    type="text"
                    id="tracking-id"
                    className="futuristic-input"
                    value={trackingId}
                    onChange={handleTrackingIdChange}
                    placeholder="Enter CID to monitor"
                  />
                </div>
              </div>

              <FuturisticButton onClick={handleMonitorCid} disabled={!trackingId || isMonitoring} color="track">
                {isMonitoring ? "MONITORING..." : "MONITOR CID"}
              </FuturisticButton>
            </div>

            <div className="monitor-results">
              <div className="results-header">MONITOR RESULT</div>
              <div className="results-container">
                {isMonitoring ? (
                  <div className="monitoring-indicator">
                    <div className="monitoring-spinner"></div>
                    <div className="monitoring-text">SCANNING BLOCKCHAIN & IPFS NETWORK</div>
                  </div>
                ) : monitoringResults ? (
                  monitoringResults.status === "success" ? (
                    <div className="log-entries">
                      {monitoringResults.results.map((entry, index) => (
                        <div key={index} className="log-entry">
                          <div className="log-icon"></div>
                          <div className="log-text">{entry}</div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="error-message">
                      {monitoringResults.message}
                      {monitoringResults.error && <div className="error-details">{monitoringResults.error}</div>}
                    </div>
                  )
                ) : (
                  <div className="no-results">
                    <div className="no-results-icon"></div>
                    <div className="no-results-text">Enter a CID to monitor access logs</div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </HolographicCard>

        <HolographicCard title="HOW TRACKING WORKS" className="info-card" glowColor="#ff00e6">
          <div className="info-content">
            <div className="info-section">
              <h3>BLOCKCHAIN VERIFICATION</h3>
              <p>
                Each protected image is invisibly watermarked and its unique identifier is securely stored on the
                blockchain, creating an immutable record of ownership.
              </p>
            </div>

            <div className="info-section">
              <h3>DECENTRALIZED STORAGE</h3>
              <p>
                Images are pinned to IPFS (InterPlanetary File System), a decentralized storage network that ensures
                your data remains accessible without relying on centralized servers.
              </p>
            </div>

            <div className="info-diagram">
              <div className="diagram-container tracking-diagram">
                <div className="diagram-image">
                  <div className="diagram-label">IMAGE</div>
                </div>
                <div className="diagram-arrow"></div>
                <div className="diagram-watermark">
                  <div className="diagram-label">WATERMARK</div>
                </div>
                <div className="diagram-arrow"></div>
                <div className="diagram-ipfs">
                  <div className="diagram-label">IPFS</div>
                </div>
                <div className="diagram-arrow"></div>
                <div className="diagram-blockchain">
                  <div className="diagram-label">BLOCKCHAIN</div>
                </div>
              </div>
            </div>
          </div>
        </HolographicCard>
      </div>
    </div>
  )
}

export default TrackPage
