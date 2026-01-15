/**
 * API client service for Smart Library backend
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Search API
export const searchAPI = {
  search: async (query, topK = 10) => {
    const response = await api.post('/api/search/', { query, top_k: topK })
    return response.data
  },
  
  rerank: async (query, positiveIds = [], negativeIds = [], topK = 10) => {
    const response = await api.post('/api/search/rerank/', {
      query,
      positive_ids: positiveIds,
      negative_ids: negativeIds,
      top_k: topK,
    })
    return response.data
  },
}

// Document API
export const documentAPI = {
  list: async (limit = 50) => {
    const response = await api.get('/api/documents/', { params: { limit } })
    return response.data
  },
  
  get: async (docId) => {
    const response = await api.get(`/api/documents/${docId}/`)
    return response.data
  },
  
  upload: async (file, onProgress = null) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/api/documents/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(percentCompleted)
        }
      }
    })
    return response.data
  },
  
  add: async (path, debug = false) => {
    const response = await api.post('/api/documents/add/', { path, debug })
    return response.data
  },
  
  delete: async (docId) => {
    const response = await api.delete(`/api/documents/${docId}/`)
    return response.data
  },
  
  getText: async (textId) => {
    const response = await api.get(`/api/documents/text/${textId}/`)
    return response.data
  },
}

// Label API
export const labelAPI = {
  label: async (resultId, label) => {
    const response = await api.post('/api/labels/', {
      result_id: resultId,
      label,
    })
    return response.data
  },
  
  getLabels: async () => {
    const response = await api.get('/api/labels/')
    return response.data
  },
  
  clearLabels: async () => {
    const response = await api.delete('/api/labels/')
    return response.data
  },
}

export default api
