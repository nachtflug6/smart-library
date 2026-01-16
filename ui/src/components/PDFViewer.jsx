import { useState, useEffect, useRef } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/Page/AnnotationLayer.css'
import 'react-pdf/dist/Page/TextLayer.css'
import './PDFViewer.css'

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`

function PDFViewer({ docId, textId, initialPage, textContent, onClose }) {
  const [numPages, setNumPages] = useState(null)
  const [scale, setScale] = useState(1.0)
  const [currentPage, setCurrentPage] = useState(1)
  const [searchText, setSearchText] = useState('')
  const contentRef = useRef(null)
  const pageRefs = useRef({})
  const searchInputRef = useRef(null)
  const pdfUrl = `/api/documents/pdf/${docId}`

  // Reset state when document changes
  useEffect(() => {
    setNumPages(null)
    setCurrentPage(1)
    setSearchText('')
    pageRefs.current = {}
  }, [docId])

  // Handle Ctrl+F keyboard shortcut
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault()
        searchInputRef.current?.focus()
      }
      if (e.key === 'Escape') {
        setSearchText('')
        searchInputRef.current?.blur()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Scroll to initial page when specified or document loads
  useEffect(() => {
    if (initialPage && numPages && initialPage <= numPages) {
      // Delay to ensure pages are rendered before scrolling
      const timer = setTimeout(() => {
        scrollToPage(initialPage)
      }, 300)
      return () => clearTimeout(timer)
    }
  }, [initialPage, numPages])

  function onDocumentLoadSuccess({ numPages }) {
    setNumPages(numPages)
  }

  const scrollToPage = (pageNum) => {
    const pageElement = pageRefs.current[pageNum]
    if (pageElement) {
      pageElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
      setCurrentPage(pageNum)
    } else {
      // Retry if element not found (page not rendered yet)
      setTimeout(() => {
        const retryElement = pageRefs.current[pageNum]
        if (retryElement) {
          retryElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
          setCurrentPage(pageNum)
        }
      }, 200)
    }
  }

  // Track which page is in view during scroll
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const pageNum = parseInt(entry.target.dataset.pageNumber)
            if (!isNaN(pageNum)) {
              setCurrentPage(pageNum)
            }
          }
        })
      },
      {
        root: contentRef.current,
        threshold: 0.5,
      }
    )

    Object.values(pageRefs.current).forEach((ref) => {
      if (ref) observer.observe(ref)
    })

    return () => observer.disconnect()
  }, [numPages])

  const handleZoomIn = () => {
    setScale(prev => Math.min(2.5, prev + 0.2))
  }

  const handleZoomOut = () => {
    setScale(prev => Math.max(0.5, prev - 0.2))
  }

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      scrollToPage(currentPage - 1)
    }
  }

  const handleNextPage = () => {
    if (currentPage < numPages) {
      scrollToPage(currentPage + 1)
    }
  }

  const handleSearchChange = (e) => {
    setSearchText(e.target.value)
  }

  const customTextRenderer = (textItem) => {
    if (!searchText.trim()) return textItem.str
    
    const searchLower = searchText.toLowerCase()
    const textLower = textItem.str.toLowerCase()
    
    if (textLower.includes(searchLower)) {
      const parts = []
      let currentIndex = 0
      let searchIndex
      
      while ((searchIndex = textLower.indexOf(searchLower, currentIndex)) !== -1) {
        // Add text before match
        if (searchIndex > currentIndex) {
          parts.push(textItem.str.substring(currentIndex, searchIndex))
        }
        // Add highlighted match
        parts.push(
          `<mark style="background-color: #ffeb3b; color: #000;">${textItem.str.substring(searchIndex, searchIndex + searchText.length)}</mark>`
        )
        currentIndex = searchIndex + searchText.length
      }
      
      // Add remaining text
      if (currentIndex < textItem.str.length) {
        parts.push(textItem.str.substring(currentIndex))
      }
      
      return parts.join('')
    }
    
    return textItem.str
  }

  return (
    <div className="pdf-viewer-panel">
      <div className="pdf-viewer-controls">
        <div className="pdf-controls-left">
          <button onClick={handleZoomOut} disabled={scale <= 0.5}>-</button>
          <span className="zoom-level">{Math.round(scale * 100)}%</span>
          <button onClick={handleZoomIn} disabled={scale >= 2.5}>+</button>
        </div>
        <div className="pdf-controls-center">
          <button onClick={handlePreviousPage} disabled={currentPage <= 1}>←</button>
          <span className="page-info">
            Page {currentPage} of {numPages || '?'}
          </span>
          <button onClick={handleNextPage} disabled={currentPage >= numPages}>→</button>
        </div>
        <div className="pdf-controls-right">
          <div className="pdf-search-container">
            <span className="search-icon">🔍</span>
            <input
              ref={searchInputRef}
              type="text"
              value={searchText}
              onChange={handleSearchChange}
              placeholder="Search (Ctrl+F)"
              className="pdf-search-input"
            />
            {searchText && (
              <button onClick={() => setSearchText('')} className="pdf-search-clear">
                ✕
              </button>
            )}
          </div>
        </div>
      </div>
      
      <div className="pdf-viewer-content" ref={contentRef}>
        <Document
          file={pdfUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          loading={<div className="pdf-loading">Loading PDF...</div>}
          error={<div className="pdf-error">Failed to load PDF</div>}
        >
          {Array.from(new Array(numPages), (el, index) => (
            <div
              key={`page_${index + 1}`}
              ref={(el) => (pageRefs.current[index + 1] = el)}
              data-page-number={index + 1}
              className="pdf-page-container"
            >
              <Page 
                pageNumber={index + 1}
                scale={scale}
                renderTextLayer={true}
                renderAnnotationLayer={true}
                customTextRenderer={searchText.trim() ? customTextRenderer : undefined}
              />
            </div>
          ))}
        </Document>
      </div>
    </div>
  )
}

export default PDFViewer
