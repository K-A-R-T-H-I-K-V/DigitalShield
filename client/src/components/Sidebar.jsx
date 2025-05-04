import { useState, useEffect } from "react"
import { NavLink } from "react-router-dom"
import "./Sidebar.css"

const Sidebar = ({ isOpen }) => {
  const [activeIndex, setActiveIndex] = useState(null)

  const menuItems = [
    { path: "/", label: "DASHBOARD", icon: "dashboard" },
    { path: "/poison", label: "POISONING", icon: "poison" },
    { path: "/track", label: "TRACKING", icon: "track" },
    { path: "/revoke", label: "REVOKING", icon: "revoke" },
    { path: "/about", label: "ABOUT", icon: "about" },
  ]

  useEffect(() => {
    const currentPath = window.location.pathname
    const index = menuItems.findIndex((item) => item.path === currentPath)
    setActiveIndex(index >= 0 ? index : 0)
  }, [])

  return (
    <aside className={`sidebar ${isOpen ? "open" : ""}`}>
      <div className="sidebar-content">
        <div className="system-status">
          <div className="status-indicator online"></div>
          <span>SYSTEM ONLINE</span>
        </div>

        <nav className="sidebar-nav">
          <ul>
            {menuItems.map((item, index) => (
              <li key={index}>
                <NavLink
                  to={item.path}
                  className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                  onClick={() => setActiveIndex(index)}
                >
                  <div className="nav-icon">
                    <div className={`icon-${item.icon}`}></div>
                  </div>
                  <span>{item.label}</span>
                  {index === activeIndex && (
                    <div className="active-indicator">
                      <div className="indicator-dot"></div>
                    </div>
                  )}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="system-info">
          <div className="info-item">
            <span className="info-label">VERSION</span>
            <span className="info-value">2.8.5</span>
          </div>
          <div className="info-item">
            <span className="info-label">BLOCKCHAIN</span>
            <span className="info-value">CONNECTED</span>
          </div>
          <div className="info-item">
            <span className="info-label">IPFS</span>
            <span className="info-value">ONLINE</span>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
