import { Link } from 'react-router-dom'
import './DocumentCard.css'

function DocumentCard({ document }) {
  return (
    <Link to={`/documents/${document.id}`} className="document-card">
      <div className="document-header">
        <h3 className="document-title">{document.title || 'Untitled Document'}</h3>
      </div>
      
      <div className="document-metadata">
        {document.authors && document.authors.length > 0 && (
          <div className="metadata-row">
            <span className="metadata-label">Authors:</span>
            <span className="metadata-value">
              {document.authors.slice(0, 3).join(', ')}
              {document.authors.length > 3 && ', et al.'}
            </span>
          </div>
        )}
        
        {document.year && (
          <div className="metadata-row">
            <span className="metadata-label">Year:</span>
            <span className="metadata-value">{document.year}</span>
          </div>
        )}
        
        {document.page_count && (
          <div className="metadata-row">
            <span className="metadata-label">Pages:</span>
            <span className="metadata-value">{document.page_count}</span>
          </div>
        )}
      </div>
      
      <div className="document-footer">
        <span className="document-id">{document.id}</span>
      </div>
    </Link>
  )
}

export default DocumentCard
