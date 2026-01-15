import { useState } from 'react'
import SearchBar from '../components/SearchBar'
import SearchResults from '../components/SearchResults'
import { searchAPI, labelAPI } from '../services/api'
import './Search.css'

function Search() {
  const [results, setResults] = useState([])
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = async (searchQuery, topK) => {
    setIsLoading(true)
    setError(null)
    setQuery(searchQuery)
    
    try {
      const data = await searchAPI.search(searchQuery, topK)
      setResults(data.results)
    } catch (err) {
      setError('Search failed. Please try again.')
      console.error('Search error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRerank = async () => {
    if (!query) return
    
    setIsLoading(true)
    setError(null)
    
    try {
      // Get current labels
      const labels = await labelAPI.getLabels()
      
      // Rerank with current labels
      const data = await searchAPI.rerank(
        query,
        labels.positive_ids,
        labels.negative_ids,
        results.length || 10
      )
      
      setResults(data.results)
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
        <SearchResults
          results={results}
          query={query}
          onRerank={handleRerank}
        />
      )}
    </div>
  )
}

export default Search
