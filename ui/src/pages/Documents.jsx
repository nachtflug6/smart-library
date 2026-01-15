import { useState, useEffect } from 'react'
import { documentAPI } from '../services/api'
import './Documents.css'

function Documents() {
  const [documents, setDocuments] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadMessage, setUploadMessage] = useState(null)
  const [sortField, setSortField] = useState('title')
  const [sortOrder, setSortOrder] = useState('asc')

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const data = await documentAPI.list()
      setDocuments(data.documents)
    } catch (err) {
      setError('Failed to load documents. Please try again.')
      console.error('Load documents error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSort = (field) => {
    if (sortField === field) {
      // Toggle sort order if clicking the same field
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      // New field, default to ascending
      setSortField(field)
      setSortOrder('asc')
    }
  }

  const getSortedDocuments = () => {
    const sorted = [...documents].sort((a, b) => {
      let aVal, bVal

      switch (sortField) {
        case 'title':
          aVal = (a.title || '').toLowerCase()
          bVal = (b.title || '').toLowerCase()
          break
        case 'year':
          aVal = a.year || 0
          bVal = b.year || 0
          break
        case 'authors':
          aVal = a.authors?.[0]?.toLowerCase() || ''
          bVal = b.authors?.[0]?.toLowerCase() || ''
          break
        case 'created':
          aVal = a.created_at || ''
          bVal = b.created_at || ''
          break
        default:
          aVal = a.id
          bVal = b.id
      }

      if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1
      if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1
      return 0
    })

    return sorted
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (!file.name.endsWith('.pdf')) {
      setUploadMessage({ type: 'error', text: 'Please select a PDF file' })
      return
    }

    setIsUploading(true)
    setUploadProgress(0)
    setUploadMessage(null)

    try {
      const result = await documentAPI.upload(file, (progress) => {
        setUploadProgress(progress)
      })

      if (result.success) {
        setUploadMessage({ 
          type: 'success', 
          text: `Successfully uploaded: ${file.name}` 
        })
        // Reload documents list
        await loadDocuments()
      } else {
        setUploadMessage({ 
          type: 'error', 
          text: result.message || 'Upload failed' 
        })
      }
    } catch (err) {
      setUploadMessage({ 
        type: 'error', 
        text: 'Upload failed. Please try again.' 
      })
      console.error('Upload error:', err)
    } finally {
      setIsUploading(false)
      setUploadProgress(0)
      // Reset file input
      event.target.value = ''
    }
  }

  const handleDelete = async (docId) => {
    if (!confirm('Are you sure you want to delete this document?')) {
      return
    }
    
    try {
      await documentAPI.delete(docId)
      setDocuments(documents.filter(doc => doc.id !== docId))
    } catch (err) {
      alert('Failed to delete document. Please try again.')
      console.error('Delete error:', err)
    }
  }

  const getSortIndicator = (field) => {
    if (sortField !== field) return ''
    return sortOrder === 'asc' ? ' ▲' : ' ▼'
  }

  if (isLoading) {
    return (
      <div className="documents-page">
        <div className="loading">Loading documents...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="documents-page">
        <div className="error-message">{error}</div>
        <button onClick={loadDocuments} className="retry-button">
          Retry
        </button>
      </div>
    )
  }

  const sortedDocuments = getSortedDocuments()

  return (
    <div className="documents-page">
      <div className="documents-header">
        <h1>Document Library</h1>
        <p className="subtitle">
          {documents.length} document{documents.length !== 1 ? 's' : ''} in your library
        </p>
      </div>

      <div className="upload-section">
        <div className="upload-container">
          <label htmlFor="file-upload" className="upload-button">
            {isUploading ? 'Uploading...' : '📄 Upload PDF'}
          </label>
          <input
            id="file-upload"
            type="file"
            accept=".pdf"
            onChange={handleFileUpload}
            disabled={isUploading}
            style={{ display: 'none' }}
          />
          {isUploading && (
            <div className="upload-progress">
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <span className="progress-text">{uploadProgress}%</span>
            </div>
          )}
          {uploadMessage && (
            <div className={`upload-message ${uploadMessage.type}`}>
              {uploadMessage.text}
            </div>
          )}
        </div>
      </div>
      
      {documents.length === 0 ? (
        <div className="no-documents">
          <p>No documents found. Add documents using the CLI:</p>
          <code>smartlib add /path/to/document.pdf</code>
        </div>
      ) : (
        <div className="documents-list-container">
          <table className="documents-table">
            <thead>
              <tr>
                <th onClick={() => handleSort('title')} className="sortable">
                  Title {getSortIndicator('title')}
                </th>
                <th onClick={() => handleSort('authors')} className="sortable">
                  Author {getSortIndicator('authors')}
                </th>
                <th onClick={() => handleSort('year')} className="sortable year-col">
                  Year {getSortIndicator('year')}
                </th>
                <th className="id-col">ID</th>
                <th className="actions-col">Actions</th>
              </tr>
            </thead>
            <tbody>
              {sortedDocuments.map((doc) => (
                <tr key={doc.id} className="document-row">
                  <td className="title-cell">
                    <div className="title-content">
                      <strong>{doc.title || 'Untitled'}</strong>
                      {doc.doi && (
                        <a 
                          href={`https://doi.org/${doc.doi}`} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="doi-link"
                        >
                          {doc.doi}
                        </a>
                      )}
                    </div>
                  </td>
                  <td className="author-cell">
                    {doc.authors && doc.authors.length > 0 
                      ? doc.authors.slice(0, 2).join(', ') + (doc.authors.length > 2 ? ' et al.' : '')
                      : '-'
                    }
                  </td>
                  <td className="year-cell">{doc.year || '-'}</td>
                  <td className="id-cell" title={doc.id}>
                    <code>{doc.id.slice(0, 12)}...</code>
                  </td>
                  <td className="action-cell">
                    <button
                      className="delete-btn"
                      onClick={() => handleDelete(doc.id)}
                      title="Delete"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default Documents
