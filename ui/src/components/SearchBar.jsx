import { useState } from 'react'
import './SearchBar.css'

function SearchBar({ onSearch, isLoading }) {
  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(10)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query, topK)
    }
  }

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <div className="search-input-group">
        <input
          type="text"
          className="search-input"
          placeholder="Search for papers, concepts, or topics..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={isLoading}
        />
        <input
          type="number"
          className="topk-input"
          min="1"
          max="100"
          value={topK}
          onChange={(e) => setTopK(parseInt(e.target.value))}
          disabled={isLoading}
          title="Number of results"
        />
        <button
          type="submit"
          className="search-button"
          disabled={isLoading || !query.trim()}
        >
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </div>
    </form>
  )
}

export default SearchBar
