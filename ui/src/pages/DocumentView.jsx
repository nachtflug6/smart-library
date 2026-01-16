import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { documentAPI } from '../services/api'
import PDFViewer from '../components/PDFViewer'
import './DocumentView.css'

function DocumentView() {
  const { id } = useParams()
  const [document, setDocument] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadDocument()
  }, [id])

  const loadDocument = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const data = await documentAPI.get(id)
      setDocument(data)
    } catch (err) {
      setError('Failed to load document. Please try again.')
      console.error('Load document error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="document-view">
        <div className="loading">Loading document...</div>
      </div>
    )
  }

  if (error || !document) {
    return (
      <div className="document-view">
        <div className="error-message">{error || 'Document not found'}</div>
        <Link to="/documents" className="back-link">← Back to Documents</Link>
      </div>
    )
  }

  return (
    <div className="document-view">
      <Link to="/documents" className="back-link">← Back to Documents</Link>
      
      <div className="document-details">
        <h1 className="document-title">{document.title || 'Untitled Document'}</h1>
        
        <div className="metadata-grid">
          {document.authors && document.authors.length > 0 && (
            <div className="metadata-item">
              <span className="metadata-label">Authors</span>
              <span className="metadata-value">
                {document.authors.join(', ')}
              </span>
            </div>
          )}
          
          {document.year && (
            <div className="metadata-item">
              <span className="metadata-label">Year</span>
              <span className="metadata-value">{document.year}</span>
            </div>
          )}
          
          {document.doi && (
            <div className="metadata-item">
              <span className="metadata-label">DOI</span>
              <span className="metadata-value">
                <a href={`https://doi.org/${document.doi}`} target="_blank" rel="noopener noreferrer">
                  {document.doi}
                </a>
              </span>
            </div>
          )}
          
          {document.page_count && (
            <div className="metadata-item">
              <span className="metadata-label">Pages</span>
              <span className="metadata-value">{document.page_count}</span>
            </div>
          )}
          
          {document.source_path && (
            <div className="metadata-item full-width">
              <span className="metadata-label">Source</span>
              <span className="metadata-value code">{document.source_path}</span>
            </div>
          )}
        </div>
        
        {document.abstract && (
          <div className="abstract-section">
            <h2>Abstract</h2>
            <p className="abstract-text">{document.abstract}</p>
          </div>
        )}
        
        <div className="document-id-section">
          <span className="metadata-label">Document ID:</span>
          <code className="document-id">{document.id}</code>
        </div>
      </div>
      
      <div className="pdf-viewer-section">
        <h2>PDF Viewer</h2>
        <PDFViewer docId={document.id} />
      </div>
    </div>
  )
}

export default DocumentView
