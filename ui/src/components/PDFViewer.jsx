import './PDFViewer.css'

function PDFViewer({ docId, textId, initialPage, textContent, onClose }) {
  const pdfUrl = `/api/documents/pdf/${docId}`

  return (
    <div className="pdf-viewer-panel">
      {/* PDF Content */}
      <div className="pdf-viewer-content">
        <embed
          src={pdfUrl}
          type="application/pdf"
          title={`PDF Viewer - Page ${initialPage || 1}`}
          style={{
            width: '100%',
            height: '100%',
            border: 'none',
          }}
        />
      </div>
    </div>
  )
}

export default PDFViewer
