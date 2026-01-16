import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import Search from './pages/Search'
import Documents from './pages/Documents'
import DocumentView from './pages/DocumentView'
import './App.css'

function App() {
  return (
    <Router>
      <AppShell />
    </Router>
  )
}

function AppShell() {
  const navigate = useNavigate()
  const [navQuery, setNavQuery] = useState('')

  const handleNavSearch = (e) => {
    e.preventDefault()
    const q = navQuery.trim()
    if (!q) return
    navigate(`/?q=${encodeURIComponent(q)}`)
  }

  const handleNavUpload = () => {
    navigate('/documents', { state: { openUpload: true } })
  }

  return (
    <div className="app">
      <nav className="navbar">
        <div className="nav-container">
          <div className="nav-left">
            <Link to="/" className="nav-brand">Smart Library</Link>
          </div>

          <div className="nav-center">
            <form className="nav-search" onSubmit={handleNavSearch}>
              <input
                type="text"
                placeholder="Search documents..."
                value={navQuery}
                onChange={(e) => setNavQuery(e.target.value)}
              />
              <button type="submit">Search</button>
            </form>
          </div>

          <div className="nav-actions">
            <button className="nav-upload" onClick={handleNavUpload}>
              Upload PDF
            </button>

            <Link to="/documents" className="nav-link">Documents</Link>
          </div>
        </div>
      </nav>
      
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Search />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/documents/:id" element={<DocumentView />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
