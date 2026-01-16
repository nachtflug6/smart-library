import { useState, useEffect, useRef } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { documentAPI } from '../services/api'
import Pagination from '../components/Pagination'
import PDFViewer from '../components/PDFViewer'
import { setGlobalUploadState } from '../App'
import './Documents.css'

function Documents() {
  const [documents, setDocuments] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadMessage, setUploadMessage] = useState(null)
  const [uploadStats, setUploadStats] = useState({ total: 0, completed: 0, failed: 0 })
  const [sortField, setSortField] = useState('title')
  const [sortOrder, setSortOrder] = useState('asc')
  const [currentPage, setCurrentPage] = useState(1)
  const [selectedDocId, setSelectedDocId] = useState(null)
  const fileInputRef = useRef(null)
  const location = useLocation()
  const navigate = useNavigate()
  const PAGE_SIZE = 20

  // Open file picker when navigated from nav upload
  useEffect(() => {
    if (location.state?.openUpload && fileInputRef.current) {
      fileInputRef.current.click()
      navigate(location.pathname, { replace: true, state: {} })
    }
  }, [location.state, location.pathname, navigate])

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const data = await documentAPI.list()
      setDocuments(data.documents)
      setCurrentPage(1)
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
    setCurrentPage(1)
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

  const getPagedDocuments = () => {
    const sorted = getSortedDocuments()
    const startIndex = (currentPage - 1) * PAGE_SIZE
    const endIndex = startIndex + PAGE_SIZE
    return sorted.slice(startIndex, endIndex)
  }

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files || [])
    if (files.length === 0) return

    // Validate all files are PDFs
    const invalidFiles = files.filter(f => !f.name.endsWith('.pdf'))
    if (invalidFiles.length > 0) {
      setUploadMessage({ 
        type: 'error', 
        text: `${invalidFiles.length} file(s) are not PDFs. Please select only PDF files.` 
      })
      event.target.value = ''
      return
    }

    setIsUploading(true)
    setUploadProgress(0)
    setUploadMessage(null)
    setUploadStats({ total: files.length, completed: 0, failed: 0 })
    setGlobalUploadState({ isUploading: true, progress: 0 })

    const results = []
    
    try {
      // Upload files sequentially
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        try {
          const result = await documentAPI.upload(file, (progress) => {
            // Show overall progress
            const overallProgress = Math.round(
              ((i + progress / 100) / files.length) * 100
            )
            setUploadProgress(overallProgress)
            setGlobalUploadState({ isUploading: true, progress: overallProgress })
          })

          if (result.success) {
            results.push({ name: file.name, success: true })
            setUploadStats(prev => ({ ...prev, completed: prev.completed + 1 }))
          } else {
            results.push({ name: file.name, success: false, error: result.message })
            setUploadStats(prev => ({ ...prev, failed: prev.failed + 1 }))
          }
        } catch (err) {
          results.push({ name: file.name, success: false, error: err.message })
          setUploadStats(prev => ({ ...prev, failed: prev.failed + 1 }))
        }
      }

      // Generate summary message
      const successful = results.filter(r => r.success).length
      const failed = results.filter(r => !r.success).length

      if (failed === 0) {
        setUploadMessage({
          type: 'success',
          text: `Successfully uploaded ${successful} file${successful !== 1 ? 's' : ''}`
        })
      } else if (successful === 0) {
        setUploadMessage({
          type: 'error',
          text: `Failed to upload ${failed} file${failed !== 1 ? 's' : ''}`
        })
      } else {
        setUploadMessage({
          type: 'warning',
          text: `Uploaded ${successful} file${successful !== 1 ? 's' : ''}, ${failed} failed`
        })
      }

      // Reload documents list
      await loadDocuments()
    } catch (err) {
      setUploadMessage({
        type: 'error',
        text: 'Upload process failed. Please try again.'
      })
      console.error('Upload error:', err)
    } finally {
      setIsUploading(false)
      setUploadProgress(0)
      setUploadStats({ total: 0, completed: 0, failed: 0 })
      setGlobalUploadState({ isUploading: false, progress: 0 })
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

  const handleViewDocument = (docId) => {
    setSelectedDocId(docId)
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
  const pagedDocuments = getPagedDocuments()
  const totalPages = Math.max(1, Math.ceil(sortedDocuments.length / PAGE_SIZE))
  const showingStart = (currentPage - 1) * PAGE_SIZE + 1
  const showingEnd = Math.min(currentPage * PAGE_SIZE, sortedDocuments.length)

  return (
    <div className="documents-page">
      <input
        ref={fileInputRef}
        id="file-upload"
        type="file"
        accept=".pdf"
        multiple
        onChange={handleFileUpload}
        disabled={isUploading}
        style={{ display: 'none' }}
      />

      {(isUploading || uploadMessage) && (
        <div className="upload-status-inline">
          {isUploading && (
            <div className="upload-progress compact">
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
      )}

      {documents.length === 0 ? (
        <div className="documents-layout no-data">
          <div className="no-documents">
            <p>No documents found. Add documents using the CLI:</p>
            <code>smartlib add /path/to/document.pdf</code>
          </div>
          <div className="pdf-column">
            <div className="pdf-placeholder">
              <p>Upload a document to preview it here</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="documents-layout">
          <div className="documents-column">
            <div className="documents-list-wrapper">
              <div className="documents-list-header">
                <span>
                  Showing {showingStart}-{showingEnd} of {sortedDocuments.length}
                </span>
              </div>
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
                    {pagedDocuments.map((doc) => (
                      <tr key={doc.id} className="document-row">
                        <td className="title-cell" title={doc.title || 'Untitled'}>
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
                        <td 
                          className="author-cell"
                          title={doc.authors && doc.authors.length > 0 ? doc.authors.join(', ') : '-'}
                        >
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
                          <div className="action-buttons">
                            <button
                              className="view-btn"
                              onClick={() => handleViewDocument(doc.id)}
                              title="View PDF"
                            >
                              View
                            </button>
                            <button
                              className="delete-btn"
                              onClick={() => handleDelete(doc.id)}
                              title="Delete"
                            >
                              🗑️
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={(page) => setCurrentPage(page)}
              />
            </div>
          </div>

          <div className="pdf-column">
            {selectedDocId ? (
              <PDFViewer
                docId={selectedDocId}
                onClose={() => setSelectedDocId(null)}
              />
            ) : (
              <div className="pdf-placeholder">
                <p>Select a document to view PDF</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default Documents
