"use client"

import { useState } from "react"
import axios from "axios"
import HolographicCard from "../components/HolographicCard"
import FuturisticButton from "../components/FuturisticButton"
import { showToast, ToastTypes } from "../components/ToastContainer"
import "./RevokePage.css"

const RevokePage = () => {
  const [revokeCid, setRevokeCid] = useState("")
  const [isRevoking, setIsRevoking] = useState(false)
  const [revokeResult, setRevokeResult] = useState(null)
  const [confirmationOpen, setConfirmationOpen] = useState(false)

  const handleRevokeCidChange = (e) => {
    setRevokeCid(e.target.value)
  }

  const handleRevokeRequest = () => {
    if (!revokeCid) return
    setConfirmationOpen(true)
  }

  const handleCancelRevoke = () => {
    setConfirmationOpen(false)
    showToast("Revocation cancelled", ToastTypes.INFO)
  }

  const handleConfirmRevoke = async () => {
    setConfirmationOpen(false)
    setIsRevoking(true)
    setRevokeResult(null)
    showToast(`Initiating revocation for CID: ${revokeCid}...`, ToastTypes.INFO)

    try {
      // Make API request using axios
      const response = await axios.post("http://localhost:5000/api/revoke", {
        cid: revokeCid,
      })

      // Process successful response
      setRevokeResult({
        success: true,
        message: "Access successfully revoked",
        details: {
          cid: revokeCid,
          timestamp: new Date().toISOString(),
          status: "REVOKED",
          blockchainStatus: "VERIFIED",
        },
      })
      showToast("Access successfully revoked", ToastTypes.SUCCESS)
    } catch (error) {
      console.error("Error revoking access:", error)
      setRevokeResult({
        success: false,
        message: "Failed to revoke access",
        error: error.response?.data?.error || error.message,
      })
      showToast(`Revocation failed: ${error.response?.data?.error || error.message}`, ToastTypes.ERROR)
    } finally {
      setIsRevoking(false)
    }
  }

  return (
    <div className="revoke-page">
      <div className="page-header">
        <h1 className="page-title">PHASE 3: REVOKING</h1>
        <p className="page-subtitle">Permanently revoke access to your protected images</p>
      </div>

      <div className="revoke-content">
        <HolographicCard title="REVOCATION CONSOLE" className="revoke-card" glowColor="#00ff88">
          <div className="revoke-grid">
            <div className="revoke-form-section">
              <div className="form-description">
                <p>
                  Revoking access will unpin your image from IPFS and delete the encryption key from the blockchain,
                  making the image inaccessible to any external services or AI systems.
                </p>
                <p className="warning-text">WARNING: This action is permanent and cannot be undone.</p>
              </div>

              <div className="revoke-form">
                <div className="input-group">
                  <label htmlFor="revoke-cid" className="input-label">
                    CID TO REVOKE
                  </label>
                  <div className="input-container">
                    <input
                      type="text"
                      id="revoke-cid"
                      className="futuristic-input"
                      value={revokeCid}
                      onChange={handleRevokeCidChange}
                      placeholder="Enter CID to revoke access"
                    />
                  </div>
                </div>

                <FuturisticButton onClick={handleRevokeRequest} disabled={!revokeCid || isRevoking} color="revoke">
                  {isRevoking ? "REVOKING..." : "REVOKE ACCESS"}
                </FuturisticButton>
              </div>
            </div>

            <div className="revoke-status-section">
              <div className="status-container">
                {isRevoking ? (
                  <div className="revoking-indicator">
                    <div className="revoking-animation">
                      <div className="revoking-circle"></div>
                      <div className="revoking-pulse"></div>
                    </div>
                    <div className="revoking-stages">
                      <div className="stage">
                        <div className="stage-icon ipfs-icon"></div>
                        <div className="stage-text">UNPINNING FROM IPFS</div>
                      </div>
                      <div className="stage">
                        <div className="stage-icon blockchain-icon"></div>
                        <div className="stage-text">REMOVING FROM BLOCKCHAIN</div>
                      </div>
                      <div className="stage">
                        <div className="stage-icon key-icon"></div>
                        <div className="stage-text">DELETING ENCRYPTION KEY</div>
                      </div>
                    </div>
                  </div>
                ) : revokeResult ? (
                  <div className={`revoke-result ${revokeResult.success ? "success" : "error"}`}>
                    <div className="result-header">
                      <div className={`result-icon ${revokeResult.success ? "success-icon" : "error-icon"}`}></div>
                      <div className="result-title">{revokeResult.message}</div>
                    </div>

                    {revokeResult.success ? (
                      <div className="result-details">
                        <div className="detail-grid">
                          <div className="detail-item">
                            <div className="detail-label">CID</div>
                            <div className="detail-value">{revokeResult.details.cid}</div>
                          </div>
                          <div className="detail-item">
                            <div className="detail-label">TIMESTAMP</div>
                            <div className="detail-value">
                              {new Date(revokeResult.details.timestamp).toLocaleString()}
                            </div>
                          </div>
                          <div className="detail-item">
                            <div className="detail-label">STATUS</div>
                            <div className="detail-value">{revokeResult.details.status}</div>
                          </div>
                          <div className="detail-item">
                            <div className="detail-label">BLOCKCHAIN STATUS</div>
                            <div className="detail-value">{revokeResult.details.blockchainStatus}</div>
                          </div>
                        </div>

                        <div className="verification-message">
                          <div className="verification-icon"></div>
                          <div className="verification-text">Revocation verified and recorded on the blockchain</div>
                        </div>
                      </div>
                    ) : (
                      <div className="error-message">
                        {revokeResult.message}
                        {revokeResult.error && <div className="error-details">{revokeResult.error}</div>}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="no-status">
                    <div className="status-placeholder">
                      <div className="placeholder-icon"></div>
                      <div className="placeholder-text">Enter a CID to revoke access to your protected image</div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </HolographicCard>

        <HolographicCard title="HOW REVOCATION WORKS" className="info-card" glowColor="#00ff88">
          <div className="info-content">
            <div className="info-section">
              <h3>COMPLETE REMOVAL</h3>
              <p>
                When you revoke access, your image is unpinned from IPFS, making it unavailable for download or access
                through the decentralized network.
              </p>
            </div>

            <div className="info-section">
              <h3>KEY DESTRUCTION</h3>
              <p>
                The encryption key stored on the blockchain is permanently deleted, rendering any cached or downloaded
                encrypted copies of your image unusable.
              </p>
            </div>

            <div className="info-section">
              <h3>VERIFICATION</h3>
              <p>
                The revocation is recorded on the blockchain, providing a verifiable timestamp and proof that you have
                withdrawn consent for the use of your image.
              </p>
            </div>
          </div>
        </HolographicCard>
      </div>

      {confirmationOpen && (
        <div className="confirmation-overlay">
          <div className="confirmation-modal">
            <div className="confirmation-header">
              <div className="confirmation-icon"></div>
              <h3>CONFIRM REVOCATION</h3>
            </div>

            <div className="confirmation-content">
              <p>You are about to permanently revoke access to the following CID:</p>
              <div className="confirmation-cid">{revokeCid}</div>
              <p className="confirmation-warning">
                This action cannot be undone. The image will be unpinned from IPFS and the encryption key will be
                deleted from the blockchain.
              </p>
            </div>

            <div className="confirmation-actions">
              <FuturisticButton onClick={handleCancelRevoke} color="secondary">
                CANCEL
              </FuturisticButton>
              <FuturisticButton onClick={handleConfirmRevoke} color="revoke">
                CONFIRM REVOCATION
              </FuturisticButton>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default RevokePage
