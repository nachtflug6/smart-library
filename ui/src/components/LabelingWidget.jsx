import { useState } from 'react'
import { labelAPI } from '../services/api'
import './LabelingWidget.css'

function LabelingWidget({ resultId, isPositive, isNegative, onLabelChange }) {
  const [loading, setLoading] = useState(false)

  const handleLabel = async (label) => {
    setLoading(true)
    try {
      await labelAPI.label(resultId, label)
      if (onLabelChange) {
        onLabelChange()
      }
    } catch (error) {
      console.error('Failed to label result:', error)
      alert('Failed to label result. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="labeling-widget">
      <button
        className={`label-button positive ${isPositive ? 'active' : ''}`}
        onClick={() => handleLabel('pos')}
        disabled={loading}
        title="Mark as positive"
      >
        👍
      </button>
      <button
        className={`label-button negative ${isNegative ? 'active' : ''}`}
        onClick={() => handleLabel('neg')}
        disabled={loading}
        title="Mark as negative"
      >
        👎
      </button>
    </div>
  )
}

export default LabelingWidget
