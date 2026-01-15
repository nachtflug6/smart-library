import { useState, useEffect } from 'react'
import './PDFViewer.css'

function PDFViewer({ docId, textId, initialPage, textContent, onClose }) {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  const pdfUrl = `/api/documents/pdf/${docId}#page=${initialPage || 1}`

  return (
    <div className="pdf-viewer-panel">
      {/* PDF Content */}
      <div className="pdf-viewer-content">
        {error && (
          <div className="pdf-error">
            <p>Error loading PDF: {error}</p>
            <p>
              <a href={pdfUrl} download target="_blank" rel="noopener noreferrer">
                Download PDF instead
              </a>
            </p>
          </div>
        )}
        
        {!error && (
          <iframe
            src={pdfUrl}
            onLoad={() => setIsLoading(false)}
            onError={() => {
              setError('Failed to load PDF viewer')
            }}
            title={`PDF Viewer - Page ${initialPage || 1}`}
          />
        )}
        
        {isLoading && !error && (
          <div className="pdf-loading">
            <div className="pdf-loading-spinner"></div>
            <p>Loading PDF...</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default PDFViewer
