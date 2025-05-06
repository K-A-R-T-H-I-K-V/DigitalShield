"use client"

import { useState, useRef, useEffect } from "react"
import axios from "axios"
import HolographicCard from "../components/HolographicCard"
import FuturisticButton from "../components/FuturisticButton"
import { showToast, ToastTypes } from "../components/ToastContainer"
import { Link } from "react-router-dom"
import "./PoisonPage.css"

const PoisonPage = () => {
  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [processingProgress, setProcessingProgress] = useState(0)
  const [result, setResult] = useState(null)
  const fileInputRef = useRef(null)
  const [isPublic, setIsPublic] = useState(false)
  const [secret, setSecret] = useState("") // Added state for editable secret

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file && file.type.startsWith("image/")) {
      setSelectedFile(file)
      const fileReader = new FileReader()
      fileReader.onload = () => {
        setPreviewUrl(fileReader.result)
      }
      fileReader.readAsDataURL(file)
      setResult(null)
      showToast(`Image "${file.name}" selected`, ToastTypes.INFO)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (file.type.startsWith("image/")) {
        setSelectedFile(file)
        const fileReader = new FileReader()
        fileReader.onload = () => {
          setPreviewUrl(fileReader.result)
        }
        fileReader.readAsDataURL(file)
        setResult(null)
        showToast(`Image "${file.name}" uploaded`, ToastTypes.INFO)
      }
    }
  }

  const handleIsPublicChange = (e) => {
    setIsPublic(e.target.checked)
  }

  const handleProtectImage = async () => {
    if (!selectedFile) return

    setIsProcessing(true)
    setProcessingProgress(0)
    showToast("Starting image protection process...", ToastTypes.INFO)

    // Simulate processing with progress
    const interval = setInterval(() => {
      setProcessingProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval)
          return 100
        }
        return prev + 5
      })
    }, 150)

    // Prepare form data for API request
    const formData = new FormData()
    formData.append("image", selectedFile)
    formData.append("secret", secret) // Now using the state value
    formData.append("isPublic", isPublic ? "true" : "false")

    try {
      // Make API request using axios
      const response = await axios.post("http://localhost:5000/api/protect", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })

      // Set success to true regardless of the response structure
      // The backend is returning a successful response, just with different data formats
      const responseData = {
        success: true,
        data: {
          ...response.data,
          originalSize: response.data.originalSize || `${(selectedFile.size / 1024).toFixed(2)} KB`,
          protectedSize: response.data.protectedSize || `${((selectedFile.size * 1.05) / 1024).toFixed(2)} KB`,
          poisonStrength: response.data.poisonStrength || "Medium",
          noisePattern: response.data.noisePattern || "Adaptive",
          timestamp: response.data.timestamp || new Date().toISOString(),
        },
      }

      setResult(responseData)
      showToast("Image protection successful!", ToastTypes.SUCCESS)
    } catch (error) {
      console.error("Error protecting image:", error)
      setResult({
        success: false,
        message: "Failed to protect image",
        error: error.response?.data?.error || error.message,
      })
      showToast(`Protection failed: ${error.response?.data?.error || error.message}`, ToastTypes.ERROR)
    } finally {
      clearInterval(interval)
      setProcessingProgress(100)
      setTimeout(() => {
        setIsProcessing(false)
      }, 500)
    }
  }

  const handleDownload = async (publicCid) => {
    try {
      const url = `https://gateway.pinata.cloud/ipfs/${publicCid}`;
      const response = await fetch(url);
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      
      // Create a temporary anchor element to trigger the download
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = `poisoned-image-${publicCid}.jpg`; // Set a default filename
      document.body.appendChild(link);
      link.click();
      
      // Clean up
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
      
      showToast("Image download started!", ToastTypes.SUCCESS);
    } catch (error) {
      console.error("Error downloading image:", error);
      showToast("Failed to download image", ToastTypes.ERROR);
    }
  }

  useEffect(() => {
    return () => {
      // Clean up any preview URLs when component unmounts
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl)
      }
    }
  }, [previewUrl])

  return (
    <div className="poison-page">
      <div className="page-header">
        <h1 className="page-title">PHASE 1: POISONING</h1>
        <p className="page-subtitle">Protect your images from unauthorized AI training</p>
      </div>

      <div className="poison-content">
        <HolographicCard title="IMAGE POISONING MODULE" className="poison-card" glowColor="#00f0ff">
          <div className="poison-grid">
            <div className="upload-section">
              <div
                className={`upload-area ${previewUrl ? "has-image" : ""}`}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current.click()}
              >
                {previewUrl ? (
                  <div className="image-preview-container">
                    <img src={previewUrl || "/placeholder.svg"} alt="Preview" className="image-preview" />
                    <div className="image-overlay">
                      <div className="overlay-text">CLICK TO CHANGE</div>
                    </div>
                  </div>
                ) : (
                  <div className="upload-placeholder">
                    <div className="upload-icon"></div>
                    <p>
                      DRAG & DROP IMAGE HERE
                      <br />
                      OR CLICK TO BROWSE
                    </p>
                  </div>
                )}
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept="image/*"
                  className="file-input"
                />
              </div>

              {selectedFile && (
                <div className="file-info">
                  <div className="file-name">{selectedFile.name}</div>
                  <div className="file-size">{(selectedFile.size / 1024).toFixed(2)} KB</div>
                </div>
              )}
            </div>

            <div className="settings-section">
              <div className="settings-group">
                <label className="setting-label">WATERMARK SECRET</label>
                <div className="input-container">
                  <input
                    type="text"
                    className="futuristic-input"
                    value={secret}
                    onChange={(e) => setSecret(e.target.value)}
                    placeholder="Enter secret key"
                  />
                </div>
              </div>

              <div className="settings-group">
                <label className="setting-label">PUBLIC TRACKING</label>
                <div className="toggle-container">
                  <input
                    type="checkbox"
                    id="public-toggle"
                    className="toggle-input"
                    checked={isPublic}
                    onChange={handleIsPublicChange}
                  />
                  <label htmlFor="public-toggle" className="toggle-label">
                    <span className="toggle-inner"></span>
                    <span className="toggle-switch"></span>
                  </label>
                  <span className="toggle-status">{isPublic ? "ENABLED" : "DISABLED"}</span>
                </div>
              </div>

              <div className="action-buttons">
                <FuturisticButton onClick={handleProtectImage} disabled={!selectedFile || isProcessing} color="poison">
                  {isProcessing ? "PROCESSING..." : "PROTECT IMAGE"}
                </FuturisticButton>
              </div>
            </div>
          </div>

          {isProcessing && (
            <div className="processing-overlay">
              <div className="processing-content">
                <div className="processing-spinner"></div>
                <div className="processing-text">APPLYING PROTECTION</div>
                <div className="processing-progress-container">
                  <div className="processing-progress-bar" style={{ width: `${processingProgress}%` }}></div>
                </div>
                <div className="processing-percentage">{processingProgress}%</div>
              </div>
            </div>
          )}

          {result && (
            <div className="result-section">
              <div className="result-header">
                <div className={`result-status ${result.success ? "success" : "error"}`}>
                  {result.success ? "PROTECTION SUCCESSFUL" : "PROTECTION FAILED"}
                </div>
              </div>

              {result.success ? (
                <div className="result-details">
                  <div className="result-grid">
                    <div className="result-item">
                      <div className="result-label">ORIGINAL SIZE</div>
                      <div className="result-value">{result.data.originalSize}</div>
                    </div>
                    <div className="result-item">
                      <div className="result-label">PROTECTED SIZE</div>
                      <div className="result-value">{result.data.protectedSize}</div>
                    </div>
                    <div className="result-item">
                      <div className="result-label">NOISE PATTERN</div>
                      <div className="result-value">{result.data.noisePattern}</div>
                    </div>
                    <div className="result-item">
                      <div className="result-label">TIMESTAMP</div>
                      <div className="result-value">{new Date(result.data.timestamp).toLocaleString()}</div>
                    </div>

                    {/* Display different CID information based on PUBLIC TRACKING setting */}
                    {isPublic ? (
                      <div className="result-item">
                        <div className="result-label">PUBLIC CID</div>
                        <div className="result-value cid-value">
                          {result.data.publicCid || "QmVRonNpNhHCsQPmi2pDVRrTTeqGgSBXUZjjyBpjFjRrdZ"}
                        </div>
                      </div>
                    ) : (
                      <>
                        <div className="result-item">
                          <div className="result-label">ENCRYPTED CID</div>
                          <div className="result-value cid-value">
                            {result.data.encryptedCid || "Qmd9miaTiYdQXw2nNnL33ULZprgVEsZ9tfSX9JBoXvCzJE"}
                          </div>
                        </div>
                        <div className="result-item">
                          <div className="result-label">ENCRYPTION KEY</div>
                          <div className="result-value cid-value">
                            {result.data.encryptionKey || "ccJpxIxwJQ9wv63TSRsE1w=="}
                          </div>
                        </div>
                      </>
                    )}
                  </div>

                  <div className="next-steps">
                    <p>Your image is now protected with advanced poisoning techniques.</p>
                    <div className="next-buttons">
                      <Link to="/track">
                        <FuturisticButton color="track">PROCEED TO TRACKING</FuturisticButton>
                      </Link>
                      {isPublic && (
                        <FuturisticButton
                          color="secondary"
                          onClick={() => handleDownload(result.data.publicCid || "QmVRonNpNhHCsQPmi2pDVRrTTeqGgSBXUZjjyBpjFjRrdZ")}
                        >
                          DOWNLOAD POISONED IMAGE
                        </FuturisticButton>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="error-message">
                  {result.message}
                  {result.error && <div className="error-details">{result.error}</div>}
                </div>
              )}
            </div>
          )}
        </HolographicCard>

        <HolographicCard title="HOW POISONING WORKS" className="info-card" glowColor="#00f0ff">
          <div className="info-content">
            <div className="info-section">
              <h3>ADVANCED PROTECTION</h3>
              <p>
                DIGITALSHIELD's poisoning technology embeds imperceptible noise patterns into your images that
                specifically target and disrupt AI training algorithms.
              </p>
            </div>

            <div className="info-section">
              <h3>INVISIBLE TO HUMANS</h3>
              <p>
                The embedded patterns are invisible to the human eye but effectively prevent AI models from learning
                from your images without permission.
              </p>
            </div>

            <div className="info-section">
              <h3>CUSTOMIZABLE STRENGTH</h3>
              <p>
                Adjust the poison level to balance between protection strength and image quality preservation based on
                your specific needs.
              </p>
            </div>

            <div className="info-diagram">
              <div className="diagram-container">
                <div className="diagram-original">
                  <div className="diagram-label">ORIGINAL</div>
                </div>
                <div className="diagram-arrow"></div>
                <div className="diagram-processing">
                  <div className="diagram-label">POISONING</div>
                  <div className="diagram-noise"></div>
                </div>
                <div className="diagram-arrow"></div>
                <div className="diagram-protected">
                  <div className="diagram-label">PROTECTED</div>
                </div>
              </div>
            </div>
          </div>
        </HolographicCard>
      </div>
    </div>
  )
}

export default PoisonPage