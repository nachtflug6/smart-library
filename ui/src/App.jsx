import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Search from './pages/Search'
import Documents from './pages/Documents'
import DocumentView from './pages/DocumentView'
import './App.css'

// Global upload state to share between components
let globalUploadState = { isUploading: false, progress: 0 }
const uploadListeners = new Set()

export const setGlobalUploadState = (state) => {
  globalUploadState = { ...globalUploadState, ...state }
  uploadListeners.forEach(listener => listener(globalUploadState))
}

export const subscribeToUploadState = (listener) => {
  uploadListeners.add(listener)
  return () => uploadListeners.delete(listener)
}

function App() {
  return (
    <Router>
      <AppShell />
    </Router>
  )
}

function AppShell() {
  const navigate = useNavigate()
  const location = useLocation()
  const [navQuery, setNavQuery] = useState('')
  const [uploadState, setUploadState] = useState(globalUploadState)

  useEffect(() => {
    return subscribeToUploadState(setUploadState)
  }, [])

  const handleNavSearch = (e) => {
    e.preventDefault()
    const q = navQuery.trim()
    if (!q) return
    navigate(`/?q=${encodeURIComponent(q)}`)
  }

  const handleNavUpload = () => {
    navigate('/documents', { state: { openUpload: true } })
  }

  const isDocumentsPage = location.pathname === '/documents'

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
            <button 
              className="nav-upload" 
              onClick={handleNavUpload}
              disabled={uploadState.isUploading}
            >
              {uploadState.isUploading ? 'Uploading...' : 'Upload PDF'}
            </button>
            {uploadState.isUploading && !isDocumentsPage && (
              <div className="nav-upload-progress">
                <div className="nav-progress-bar">
                  <div 
                    className="nav-progress-fill" 
                    style={{ width: `${uploadState.progress}%` }}
                  />
                </div>
                <span className="nav-progress-text">{uploadState.progress}%</span>
              </div>
            )}

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
