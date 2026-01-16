import { useState, useEffect } from 'react'
import { documentAPI } from '../services/api'
import LabelingWidget from './LabelingWidget'
import './SearchResults.css'

function SearchResults({ results, query, onRerank, onSelectPdf }) {
  const [expandedResults, setExpandedResults] = useState(new Set())
  const [textCache, setTextCache] = useState({})
  const [documentCache, setDocumentCache] = useState({})
  const [loadingStates, setLoadingStates] = useState({})
  // Pre-load text metadata for all results on mount
  useEffect(() => {
    const loadTextMetadata = async () => {
      const newTextCache = {}
      const newDocumentCache = {}
      const uniqueDocIds = new Set()

      for (const result of results) {
        if (!textCache[result.id] && !loadingStates[result.id]) {
          setLoadingStates(prev => ({ ...prev, [result.id]: true }))
          try {
            const text = await documentAPI.getText(result.id)
            newTextCache[result.id] = text
            
            // Try to load document info from parent_id or metadata
            const docId = text.metadata?.document_id || text.parent_id
            if (docId && !documentCache[docId]) {
              uniqueDocIds.add(docId)
            }
          } catch (error) {
            console.error('Failed to fetch text:', error)
          }
          setLoadingStates(prev => ({ ...prev, [result.id]: false }))
        }
      }

      // Load unique documents
      for (const docId of uniqueDocIds) {
        try {
          const doc = await documentAPI.get(docId)
          newDocumentCache[docId] = doc
        } catch (error) {
          console.error('Failed to fetch document:', error)
        }
      }

      if (Object.keys(newTextCache).length > 0) {
        setTextCache(prev => ({ ...prev, ...newTextCache }))
      }
      if (Object.keys(newDocumentCache).length > 0) {
        setDocumentCache(prev => ({ ...prev, ...newDocumentCache }))
      }
    }

    if (results && results.length > 0) {
      loadTextMetadata()
    }
  }, [results])

  const toggleExpand = async (resultId) => {
    const newExpanded = new Set(expandedResults)
    
    if (newExpanded.has(resultId)) {
      newExpanded.delete(resultId)
    } else {
      newExpanded.add(resultId)
    }
    
    setExpandedResults(newExpanded)
  }

  const truncateText = (text, maxLength = 200) => {
    if (!text || text.length <= maxLength) return text
    return text.substring(0, maxLength).trim() + '...'
  }

  const getDocumentInfo = (text) => {
    if (!text) return null
    const docId = text.metadata?.document_id || text.parent_id
    return docId ? documentCache[docId] : null
  }

  const getScoreColor = (score) => {
    // Color code by decimal increments
    if (score >= 0.9) return 'score-90'
    if (score >= 0.8) return 'score-80'
    if (score >= 0.7) return 'score-70'
    if (score >= 0.6) return 'score-60'
    if (score >= 0.5) return 'score-50'
    if (score >= 0.4) return 'score-40'
    if (score >= 0.3) return 'score-30'
    if (score >= 0.2) return 'score-20'
    if (score >= 0.1) return 'score-10'
    return 'score-00'
  }

  const highlightKeywords = (text, searchQuery) => {
    if (!text || !searchQuery) return text

    // Extract words from search query (split by spaces, remove special chars)
    const keywords = searchQuery
      .toLowerCase()
      .split(/\s+/)
      .filter(word => word.length > 2) // Only highlight words with 3+ chars
      .map(word => word.replace(/[^\w]/g, ''))
      .filter(word => word.length > 0)

    if (keywords.length === 0) return text

    // Create regex pattern to match any keyword (case insensitive, word boundaries)
    const pattern = new RegExp(`\\b(${keywords.join('|')})\\b`, 'gi')

    // Split text and wrap matches in <strong> tags
    const parts = []
    let lastIndex = 0
    let match

    while ((match = pattern.exec(text)) !== null) {
      // Add text before match
      if (match.index > lastIndex) {
        parts.push(text.substring(lastIndex, match.index))
      }
      // Add highlighted match
      parts.push(<strong key={match.index}>{match[0]}</strong>)
      lastIndex = pattern.lastIndex
    }

    // Add remaining text
    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex))
    }

    return parts.length > 0 ? parts : text
  }

  if (!results || results.length === 0) {
    return (
      <div className="no-results">
        <p>No results found. Try a different search query.</p>
      </div>
    )
  }

  return (
    <div className="search-results">
      {(results.some(r => r.is_positive) || results.some(r => r.is_negative)) && (
        <div className="results-actions">
          <button onClick={onRerank} className="rerank-button">
            🔄 Rerank with Feedback
          </button>
        </div>
      )}
      
      <div className="results-list">
        {results.map((result) => {
          const text = textCache[result.id]
          const doc = text ? getDocumentInfo(text) : null
          const isExpanded = expandedResults.has(result.id)
          
          return (
            <div
              key={result.id}
              className={`result-card ${result.is_positive ? 'positive' : ''} ${result.is_negative ? 'negative' : ''}`}
            >
              {/* Compact header with document context (like CLI) */}
              <div className="result-compact-header">
                <div className="result-meta-line">
                  <span className="result-rank">#{result.rank}</span>
                  <span className={`result-score ${getScoreColor(result.score)}`}>Score: {result.score.toFixed(2)}</span>
                  {text && text.page_number && (
                    <span className="result-page">Page {text.page_number}</span>
                  )}
                  {doc && (
                    <>
                      {doc.title && (
                        <span className="result-doc-title" title={doc.title}>
                          {truncateText(doc.title, 50)}
                        </span>
                      )}
                      {doc.authors && doc.authors.length > 0 && (
                        <span className="result-author">
                          {doc.authors[0]}{doc.authors.length > 1 ? ' et al.' : ''}
                        </span>
                      )}
                      {doc.year && (
                        <span className="result-year">({doc.year})</span>
                      )}
                    </>
                  )}
                </div>
                
                {/* Content preview (always shown like CLI) */}
                {text && (
                  <div className="result-preview">
                    {highlightKeywords(text.display_content || text.content, query)}
                  </div>
                )}
              </div>

              {/* Action buttons */}
              <div className="result-actions">
                <LabelingWidget
                  resultId={result.id}
                  isPositive={result.is_positive}
                  isNegative={result.is_negative}
                  onLabelChange={onRerank}
                />
                {doc && (
                  <button
                    className="pdf-button"
                    onClick={() => onSelectPdf(doc.id, result.id, text?.page_number || 1, text?.content || '')}
                    title="View PDF"
                  >
                    📄 View PDF
                  </button>
                )}
                <button
                  className="expand-button"
                  onClick={() => toggleExpand(result.id)}
                >
                  {isExpanded ? '▲ Hide Details' : '▼ Show Details'}
                </button>
              </div>

              {/* Detailed metadata when expanded */}
              {isExpanded && text && (
                <div className="result-metadata">
                  <div className="metadata-row">
                    <span className="metadata-label">Text ID:</span>
                    <span className="metadata-value">{result.id}</span>
                  </div>
                  {text.text_type && (
                    <div className="metadata-row">
                      <span className="metadata-label">Type:</span>
                      <span className="metadata-value">{text.text_type}</span>
                    </div>
                  )}
                  {text.character_count && (
                    <div className="metadata-row">
                      <span className="metadata-label">Characters:</span>
                      <span className="metadata-value">{text.character_count}</span>
                    </div>
                  )}
                  {doc && (
                    <>
                      <div className="metadata-row">
                        <span className="metadata-label">Document:</span>
                        <span className="metadata-value">{doc.title || doc.id}</span>
                      </div>
                      {doc.doi && (
                        <div className="metadata-row">
                          <span className="metadata-label">DOI:</span>
                          <span className="metadata-value">
                            <a href={`https://doi.org/${doc.doi}`} target="_blank" rel="noopener noreferrer">
                              {doc.doi}
                            </a>
                          </span>
                        </div>
                      )}
                    </>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default SearchResults
