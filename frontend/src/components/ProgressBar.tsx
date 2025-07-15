import { CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { UploadProgress } from '../types'

interface ProgressBarProps {
  progress: UploadProgress
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ progress }) => {
  const getStatusColor = (): string => {
    switch (progress.status) {
      case 'uploading':
        return 'bg-blue-500'
      case 'analyzing':
        return 'bg-purple-500'
      case 'completed':
        return 'bg-green-500'
      case 'error':
        return 'bg-red-500'
      default:
        return 'bg-medical-300'
    }
  }

  const getStatusIcon = () => {
    switch (progress.status) {
      case 'uploading':
      case 'analyzing':
        return <Loader2 className="h-4 w-4 animate-spin" />
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-600" />
      default:
        return null
    }
  }

  const getStatusText = (): string => {
    switch (progress.status) {
      case 'uploading':
        return 'Uploading...'
      case 'analyzing':
        return 'Analyzing CT scan...'
      case 'completed':
        return 'Analysis completed'
      case 'error':
        return 'Analysis failed'
      default:
        return 'Ready'
    }
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-medical-900">
          Processing Status
        </h3>
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <span className="text-sm font-medium text-medical-700">
            {getStatusText()}
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm text-medical-600">
            {progress.message || getStatusText()}
          </span>
          <span className="text-sm font-medium text-medical-700">
            {progress.progress}%
          </span>
        </div>
        
        <div className="w-full bg-medical-200 rounded-full h-2">
          <div 
            className={`h-2 rounded-full transition-all duration-300 ${getStatusColor()}`}
            style={{ width: `${progress.progress}%` }}
          />
        </div>
      </div>

      {/* Status Steps */}
      <div className="flex items-center justify-between text-xs text-medical-600">
        <div className={`flex items-center ${progress.status === 'uploading' || progress.status === 'analyzing' || progress.status === 'completed' ? 'text-blue-600' : ''}`}>
          <div className={`w-2 h-2 rounded-full mr-2 ${progress.status === 'uploading' || progress.status === 'analyzing' || progress.status === 'completed' ? 'bg-blue-500' : 'bg-medical-300'}`} />
          Upload
        </div>
        
        <div className={`flex items-center ${progress.status === 'analyzing' || progress.status === 'completed' ? 'text-purple-600' : ''}`}>
          <div className={`w-2 h-2 rounded-full mr-2 ${progress.status === 'analyzing' || progress.status === 'completed' ? 'bg-purple-500' : 'bg-medical-300'}`} />
          Analysis
        </div>
        
        <div className={`flex items-center ${progress.status === 'completed' ? 'text-green-600' : ''}`}>
          <div className={`w-2 h-2 rounded-full mr-2 ${progress.status === 'completed' ? 'bg-green-500' : 'bg-medical-300'}`} />
          Complete
        </div>
      </div>

      {progress.status === 'error' && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <AlertCircle className="h-4 w-4 text-red-600 mr-2" />
            <span className="text-sm text-red-800">
              {progress.message || 'An error occurred during processing'}
            </span>
          </div>
        </div>
      )}
    </div>
  )
} 