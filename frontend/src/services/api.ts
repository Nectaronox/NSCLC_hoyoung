import axios from 'axios'
import { ApiResponse } from '../types'

// Configure axios defaults
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes timeout for image analysis
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    } else if (import.meta.env.DEV) {
      // Use dummy token for development
      config.headers.Authorization = `Bearer development_token_nsclc_staging_app`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login if needed
      localStorage.removeItem('auth_token')
      // You could redirect to login page here
    }
    return Promise.reject(error)
  }
)

export const apiService = {
  // Analyze CT image
  analyzeImage: async (file: File): Promise<ApiResponse> => {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await api.post('/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      return {
        success: true,
        data: response.data.data, // Extract the nested data object from the backend response
      }
    } catch (error) {
      console.error('API Error:', error)
      
      if (axios.isAxiosError(error)) {
        const errorMessage = error.response?.data?.detail || 
                           error.response?.data?.message || 
                           error.message ||
                           'Network error occurred'
        
        return {
          success: false,
          error: errorMessage,
        }
      }
      
      return {
        success: false,
        error: 'An unexpected error occurred',
      }
    }
  },

  // Health check
  healthCheck: async (): Promise<{ status: string }> => {
    try {
      const response = await api.get('/health')
      return response.data
    } catch (error) {
      throw new Error('Health check failed')
    }
  },

  // Authentication (stub for future implementation)
  login: async (credentials: { username: string; password: string }) => {
    try {
      const response = await api.post('/auth/login', credentials)
      const { token } = response.data
      
      localStorage.setItem('auth_token', token)
      
      return {
        success: true,
        data: response.data,
      }
    } catch (error) {
      return {
        success: false,
        error: 'Login failed',
      }
    }
  },

  logout: () => {
    localStorage.removeItem('auth_token')
  },

  // Get current user (stub)
  getCurrentUser: async () => {
    try {
      const response = await api.get('/auth/me')
      return response.data
    } catch (error) {
      throw new Error('Failed to get user info')
    }
  },
}

export default api 