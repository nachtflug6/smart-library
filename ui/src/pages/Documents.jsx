import { useState, useEffect } from 'react'
import DocumentCard from '../components/DocumentCard'
import { documentAPI } from '../services/api'
import './Documents.css'

function Documents() {
  const [documents, setDocuments] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadMessage, setUploadMessage] = useState(null)

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

  return (
    <div className="documents-page">
      <div className="documents-header">
        <h1>Document Library</h1>
        <p className="subtitle">
          Browse all documents in your library ({documents.length} total)
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
        <div className="documents-grid">
          {documents.map((doc) => (
            <DocumentCard key={doc.id} document={doc} />
          ))}
        </div>
      )}
    </div>
  )
}

export default Documents
