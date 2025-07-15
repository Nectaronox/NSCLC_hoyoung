import { RotateCcw, CheckCircle, AlertTriangle, Info } from 'lucide-react'
import { StagingResult } from '../types'

interface ResultsCardProps {
  result: StagingResult
  onNewCase: () => void
}

export const ResultsCard: React.FC<ResultsCardProps> = ({ result, onNewCase }) => {
  console.log('ResultsCard received props:', result); // <-- DEBUG LOG

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-50'
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  const getStageDescription = (stage: string | null): string => {
    switch (stage) {
      case 'I':
        return 'Early-stage cancer, confined to lung'
      case 'II':
        return 'Cancer spread to nearby lymph nodes'
      case 'III':
        return 'Locally advanced cancer'
      case 'IV':
        return 'Advanced cancer with distant metastases'
      default:
        return 'Stage could not be determined'
    }
  }

  const formatConfidence = (confidence: number): string => {
    return `${Math.round(confidence * 100)}%`
  }

  if (result.error) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-red-900 mb-2">Analysis Error</h3>
          <p className="text-red-700 mb-6">{result.error}</p>
          <button 
            onClick={onNewCase}
            className="btn-primary"
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Try New Case
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-medical-900">
          NSCLC Staging Results
        </h2>
        <CheckCircle className="h-6 w-6 text-green-500" />
      </div>

      {/* Overall Stage */}
      <div className="mb-6 p-4 bg-primary-50 rounded-lg border border-primary-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-primary-900">
              Overall Stage: {result.stage || 'Unknown'}
            </h3>
            <p className="text-primary-700 text-sm mt-1">
              {getStageDescription(result.stage)}
            </p>
          </div>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${getConfidenceColor(result.confidences.stage)}`}>
            {formatConfidence(result.confidences.stage)}
          </div>
        </div>
      </div>

      {/* TNM Classification */}
      <div className="space-y-4 mb-6">
        <h3 className="text-lg font-semibold text-medical-900 flex items-center">
          <Info className="h-5 w-5 mr-2" />
          TNM Classification
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* T Stage */}
          <div className="bg-medical-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-medical-900">T Stage</h4>
              <span className={`px-2 py-1 rounded text-xs font-medium ${getConfidenceColor(result.confidences.t)}`}>
                {formatConfidence(result.confidences.t)}
              </span>
            </div>
            <div className="text-2xl font-bold text-medical-900 mb-1">
              {result.t || 'Unknown'}
            </div>
            <p className="text-xs text-medical-600">Primary tumor</p>
          </div>

          {/* N Stage */}
          <div className="bg-medical-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-medical-900">N Stage</h4>
              <span className={`px-2 py-1 rounded text-xs font-medium ${getConfidenceColor(result.confidences.n)}`}>
                {formatConfidence(result.confidences.n)}
              </span>
            </div>
            <div className="text-2xl font-bold text-medical-900 mb-1">
              {result.n || 'Unknown'}
            </div>
            <p className="text-xs text-medical-600">Regional lymph nodes</p>
          </div>

          {/* M Stage */}
          <div className="bg-medical-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-medical-900">M Stage</h4>
              <span className={`px-2 py-1 rounded text-xs font-medium ${getConfidenceColor(result.confidences.m)}`}>
                {formatConfidence(result.confidences.m)}
              </span>
            </div>
            <div className="text-2xl font-bold text-medical-900 mb-1">
              {result.m || 'Unknown'}
            </div>
            <p className="text-xs text-medical-600">Distant metastases</p>
          </div>
        </div>
      </div>

      {/* Confidence Legend */}
      <div className="mb-6 p-4 bg-medical-50 rounded-lg">
        <h4 className="font-medium text-medical-900 mb-3">Confidence Levels</h4>
        <div className="flex flex-wrap gap-4 text-sm">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
            <span className="text-medical-700">High ≥80%</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
            <span className="text-medical-700">Medium 60-79%</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
            <span className="text-medical-700">Low &lt;60%</span>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end space-x-3">
        <button 
          onClick={onNewCase}
          className="btn-secondary"
        >
          <RotateCcw className="h-4 w-4 mr-2" />
          New Case
        </button>
        <button 
          onClick={() => window.print()}
          className="btn-primary"
        >
          Print Results
        </button>
      </div>

      {/* Disclaimer */}
      <div className="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
        <p className="text-xs text-amber-800">
          <strong>Important:</strong> These results are for research purposes only and should not be used for clinical diagnosis. 
          Always consult with qualified healthcare professionals for patient care decisions.
        </p>
      </div>
    </div>
  )
} 