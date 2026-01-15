import { useState } from 'react'
import SearchBar from '../components/SearchBar'
import SearchResults from '../components/SearchResults'
import Pagination from '../components/Pagination'
import { searchAPI, labelAPI } from '../services/api'
import './Search.css'

function Search() {
  const [allResults, setAllResults] = useState([]) // Store all results
  const [results, setResults] = useState([]) // Current page results
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [currentPage, setCurrentPage] = useState(1)
  const RESULTS_PER_PAGE = 10

  const handleSearch = async (searchQuery, topK) => {
    setIsLoading(true)
    setError(null)
    setQuery(searchQuery)
    setCurrentPage(1)
    
    try {
      // Fetch more results than topK for pagination (e.g., 5x the requested amount)
      const fetchAmount = Math.max(topK * 5, 50) // Fetch at least 50 for good pagination
      const data = await searchAPI.search(searchQuery, fetchAmount)
      setAllResults(data.results)
      // Show first page
      setResults(data.results.slice(0, RESULTS_PER_PAGE))
    } catch (err) {
      setError('Search failed. Please try again.')
      console.error('Search error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handlePageChange = (page) => {
    setCurrentPage(page)
    const startIndex = (page - 1) * RESULTS_PER_PAGE
    const endIndex = startIndex + RESULTS_PER_PAGE
    setResults(allResults.slice(startIndex, endIndex))
    // Scroll to top of results
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleRerank = async () => {
    if (!query) return
    
    setIsLoading(true)
    setError(null)
    
    try {
      // Get current labels
      const labels = await labelAPI.getLabels()
      
      // Rerank with current labels - use allResults length or fetch more
      const data = await searchAPI.rerank(
        query,
        labels.positive_ids,
        labels.negative_ids,
        allResults.length || 50
      )
      
      setAllResults(data.results)
      setCurrentPage(1) // Reset to first page after rerank
      // Show first page of reranked results
      setResults(data.results.slice(0, RESULTS_PER_PAGE))
    } catch (err) {
      setError('Reranking failed. Please try again.')
      console.error('Rerank error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="search-page">
      <div className="search-header">
        <h1>Search Documents</h1>
        <p className="subtitle">
          Find relevant papers and text chunks using semantic search
        </p>
      </div>
      
      <SearchBar onSearch={handleSearch} isLoading={isLoading} />
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      {isLoading && results.length === 0 && (
        <div className="loading-message">
          Searching...
        </div>
      )}
      
      {!isLoading && results.length > 0 && (
        <>
          <SearchResults
            results={results}
            query={query}
            onRerank={handleRerank}
          />
          <Pagination
            currentPage={currentPage}
            totalPages={Math.ceil(allResults.length / RESULTS_PER_PAGE)}
            onPageChange={handlePageChange}
          />
        </>
      )}
    </div>
  )
}

export default Search
