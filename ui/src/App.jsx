import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Search from './pages/Search'
import Documents from './pages/Documents'
import DocumentView from './pages/DocumentView'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-container">
            <Link to="/" className="nav-brand">Smart Library</Link>
            <div className="nav-links">
              <Link to="/">Search</Link>
              <Link to="/documents">Documents</Link>
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
    </Router>
  )
}

export default App
