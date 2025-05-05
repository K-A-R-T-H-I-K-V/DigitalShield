import HolographicCard from "../components/HolographicCard"
import "./AboutPage.css"

const AboutPage = () => {
  return (
    <div className="about-page">
      <div className="page-header">
        <h1 className="page-title">ABOUT DIGITALSHIELD</h1>
        <p className="page-subtitle">Advanced Image Protection System</p>
      </div>

      <div className="about-content">
        <HolographicCard title="SYSTEM OVERVIEW" className="overview-card">
          <div className="overview-content">
            <div className="overview-text">
              <p>
                DIGITALSHIELD is a cutting-edge image protection system designed to give users complete control over their
                digital content in an era of AI-driven data harvesting.
              </p>
              <p>
                Our three-phase approach—Poisoning, Tracking, and Revoking—provides a comprehensive solution for
                protecting your images from unauthorized use by AI training systems.
              </p>
            </div>

            <div className="system-diagram">
              <div className="diagram-node user-node">
                <div className="node-icon user-icon"></div>
                <div className="node-label">USER</div>
              </div>
              <div className="diagram-arrow"></div>
              <div className="diagram-node poison-node">
                <div className="node-icon poison-icon"></div>
                <div className="node-label">POISONING</div>
              </div>
              <div className="diagram-arrow"></div>
              <div className="diagram-node track-node">
                <div className="node-icon track-icon"></div>
                <div className="node-label">TRACKING</div>
              </div>
              <div className="diagram-arrow"></div>
              <div className="diagram-node revoke-node">
                <div className="node-icon revoke-icon"></div>
                <div className="node-label">REVOKING</div>
              </div>
              <div className="diagram-arrow"></div>
              <div className="diagram-node protection-node">
                <div className="node-icon protection-icon"></div>
                <div className="node-label">PROTECTION</div>
              </div>
            </div>
          </div>
        </HolographicCard>

        <div className="about-grid">
          <HolographicCard title="TECHNOLOGY" className="tech-card" glowColor="#00f0ff">
            <div className="tech-content">
              <div className="tech-item">
                <div className="tech-icon blockchain-tech"></div>
                <div className="tech-details">
                  <h3>BLOCKCHAIN</h3>
                  <p>
                    DIGITALSHIELD leverages advanced blockchain technology to create immutable records of image ownership
                    and track access permissions.
                  </p>
                </div>
              </div>

              <div className="tech-item">
                <div className="tech-icon ipfs-tech"></div>
                <div className="tech-details">
                  <h3>IPFS</h3>
                  <p>
                    The InterPlanetary File System provides decentralized storage, ensuring your images remain
                    accessible without relying on centralized servers.
                  </p>
                </div>
              </div>

              <div className="tech-item">
                <div className="tech-icon ai-tech"></div>
                <div className="tech-details">
                  <h3>ADVERSARIAL AI</h3>
                  <p>
                    Our poisoning techniques use advanced adversarial AI algorithms to create imperceptible patterns
                    that disrupt machine learning models.
                  </p>
                </div>
              </div>

              <div className="tech-item">
                <div className="tech-icon encryption-tech"></div>
                <div className="tech-details">
                  <h3>ENCRYPTION</h3>
                  <p>
                    DIGITALSHIELD employs next-generation encryption algorithms designed to withstand attacks from quantum
                    computers.
                  </p>
                </div>
              </div>
            </div>
          </HolographicCard>

          <HolographicCard title="PRIVACY PHILOSOPHY" className="philosophy-card" glowColor="#ff00e6">
            <div className="philosophy-content">
              <div className="philosophy-quote">
                "In the digital age, privacy is not just a right—it's a necessity."
              </div>

              <p>
                DIGITALSHIELD was created with the belief that individuals should have complete control over their digital
                content. As AI systems increasingly harvest online data without consent, we provide the tools to protect
                your creative works.
              </p>

              <p>
                Our approach balances technological innovation with ethical considerations, ensuring that your privacy
                is protected without compromising the quality or usability of your images.
              </p>

              <div className="philosophy-principles">
                <div className="principle">
                  <div className="principle-icon transparency-icon"></div>
                  <div className="principle-text">TRANSPARENCY</div>
                </div>
                <div className="principle">
                  <div className="principle-icon control-icon"></div>
                  <div className="principle-text">USER CONTROL</div>
                </div>
                <div className="principle">
                  <div className="principle-icon security-icon"></div>
                  <div className="principle-text">SECURITY</div>
                </div>
                <div className="principle">
                  <div className="principle-icon decentralization-icon"></div>
                  <div className="principle-text">DECENTRALIZATION</div>
                </div>
              </div>
            </div>
          </HolographicCard>
        </div>

        <HolographicCard title="SYSTEM SPECIFICATIONS" className="specs-card" glowColor="#00ff88">
          <div className="specs-content">
            <div className="specs-grid">
              <div className="spec-item">
                <div className="spec-label">VERSION</div>
                <div className="spec-value">2.8.5</div>
              </div>
              <div className="spec-item">
                <div className="spec-label">RELEASE DATE</div>
                <div className="spec-value">APRIL 15, 2025</div>
              </div>
              <div className="spec-item">
                <div className="spec-label">ENCRYPTION</div>
                <div className="spec-value">QUANTUM-RESISTANT AES-512</div>
              </div>
              <div className="spec-item">
                <div className="spec-label">BLOCKCHAIN</div>
                <div className="spec-value">ETHEREUM QUANTUM</div>
              </div>
              <div className="spec-item">
                <div className="spec-label">STORAGE</div>
                <div className="spec-value">IPFS v12.4</div>
              </div>
              <div className="spec-item">
                <div className="spec-label">POISONING ALGORITHM</div>
                <div className="spec-value">NEURAL DISRUPTOR v3</div>
              </div>
              <div className="spec-item">
                <div className="spec-label">WATERMARKING</div>
                <div className="spec-value">HOLOGRAPHIC STEGANOGRAPHY</div>
              </div>
              <div className="spec-item">
                <div className="spec-label">COMPATIBILITY</div>
                <div className="spec-value">ALL STANDARD IMAGE FORMATS</div>
              </div>
            </div>

            <div className="system-footer">
              <div className="footer-logo"></div>
              <div className="footer-text">DIGITALSHIELD © 2025 | ADVANCED IMAGE PROTECTION SYSTEM</div>
            </div>
          </div>
        </HolographicCard>
      </div>
    </div>
  )
}

export default AboutPage
