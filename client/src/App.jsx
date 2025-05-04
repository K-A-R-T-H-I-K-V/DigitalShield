import { useState } from "react"
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import Header from "./components/Header"
import Sidebar from "./components/Sidebar"
import Dashboard from "./pages/Dashboard"
import PoisonPage from "./pages/PoisonPage"
import TrackPage from "./pages/TrackPage"
import RevokePage from "./pages/RevokePage"
import AboutPage from "./pages/AboutPage"
import ToastContainer from "./components/ToastContainer"
import "./App.css"

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen)
  }

  return (
    <Router>
      <div className="app">
        <Header toggleSidebar={toggleSidebar} />
        <div className="content-container">
          <Sidebar isOpen={sidebarOpen} />
          <main className={`main-content ${sidebarOpen ? "sidebar-open" : ""}`}>
            <div className="holographic-overlay"></div>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/poison" element={<PoisonPage />} />
              <Route path="/track" element={<TrackPage />} />
              <Route path="/revoke" element={<RevokePage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
        <ToastContainer />
      </div>
    </Router>
  )
}

export default App
