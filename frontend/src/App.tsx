import { useState, useEffect } from 'react'
import { Activity, AlertCircle, Shield, FileImage } from 'lucide-react'
import { FileUpload } from './components/FileUpload'
import { ResultsCard } from './components/ResultsCard'
import { ProgressBar } from './components/ProgressBar'
import { StagingResult, UploadedFile, UploadProgress } from './types'
import { apiService } from './services/api'
import toast from 'react-hot-toast'


//랜딩 페이지임
function App() {
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null)
  const [result, setResult] = useState<StagingResult | null>(null)
  const [progress, setProgress] = useState<UploadProgress>({
    progress: 0,
    status: 'idle'
  })

  const handleFileUpload = async (file: UploadedFile) => {
    setUploadedFile(file)
    setResult(null)
    setProgress({ progress: 0, status: 'uploading', message: 'Uploading file...' })
    
    try {
      // Simulate upload progress
      for (let i = 0; i <= 100; i += 10) {
        setProgress(prev => ({ ...prev, progress: i }))
        await new Promise(resolve => setTimeout(resolve, 100))
      }
      
      setProgress({ progress: 100, status: 'analyzing', message: 'Analyzing CT scan...' })
      
      const response = await apiService.analyzeImage(file.file)
      console.log('API Response received:', response); // <-- DEBUG LOG
      
      if (response.success && response.data) {
        console.log('Setting result state with (only data):', response.data);
        setResult(response.data) // Ensure we are setting the result with the data object
        setProgress({ progress: 100, status: 'completed', message: 'Analysis completed' })
        toast.success('CT scan analysis completed successfully')
      } else {
        throw new Error(response.error || 'Analysis failed')
      }
    } catch (error) {
      console.error('Upload error:', error)
      setProgress({ progress: 0, status: 'error', message: 'Analysis failed' })
      toast.error(error instanceof Error ? error.message : 'Failed to analyze image')
    }
  }

  const handleNewCase = () => {
    // Clean up preview URL to prevent memory leaks
    if (uploadedFile?.preview) {
      URL.revokeObjectURL(uploadedFile.preview)
    }
    
    setUploadedFile(null)
    setResult(null)
    setProgress({ progress: 0, status: 'idle' })
    toast.success('Ready for new case')
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (uploadedFile?.preview) {
        URL.revokeObjectURL(uploadedFile.preview)
      }
    }
  }, [uploadedFile?.preview])

  return (
    <div className="min-h-screen bg-gradient-to-br from-medical-50 to-primary-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-primary-600 p-3 rounded-full mr-4">
              <Activity className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-medical-900">
              NSCLC Staging Assistant
            </h1>
          </div>
          <p className="text-medical-600 text-lg max-w-2xl mx-auto">
            AI-powered non-small-cell lung cancer staging from chest CT images
          </p>
          
          {/* Disclaimer */}
          <div className="mt-6 bg-amber-50 border border-amber-200 rounded-lg p-4 max-w-3xl mx-auto">
            <div className="flex items-start">
              <AlertCircle className="h-5 w-5 text-amber-600 mt-0.5 mr-2 flex-shrink-0" />
              <div className="text-amber-800 text-sm text-left">
                <p className="font-medium mb-1">Research Use Only</p>
                <p>This tool is for research purposes only and is not FDA-cleared for clinical diagnosis. 
                All results should be reviewed by qualified healthcare professionals.</p>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Upload Section */}
            <div className="space-y-6">
              <FileUpload 
                onFileUpload={handleFileUpload}
                uploadedFile={uploadedFile}
                isProcessing={progress.status === 'uploading' || progress.status === 'analyzing'}
              />
              
              {progress.status !== 'idle' && (
                <ProgressBar progress={progress} />
              )}
              
              {uploadedFile && (
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4 text-medical-900">
                    Uploaded File
                  </h3>
                  <div className="flex items-center space-x-4">
                    {uploadedFile.preview ? (
                      <img 
                        src={uploadedFile.preview} 
                        alt="Preview" 
                        className="w-16 h-16 object-cover rounded-lg border border-medical-200"
                      />
                    ) : (
                      <div className="w-16 h-16 bg-medical-100 rounded-lg border border-medical-200 flex items-center justify-center">
                        <FileImage className="h-8 w-8 text-medical-400" />
                      </div>
                    )}
                    <div className="flex-1">
                      <p className="font-medium text-medical-900">{uploadedFile.name}</p>
                      <p className="text-sm text-medical-600">{uploadedFile.size}</p>
                      <p className="text-sm text-medical-600">{uploadedFile.type}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Results Section */}
            <div className="space-y-6">
              {result && (
                <ResultsCard 
                  result={result}
                  onNewCase={handleNewCase}
                />
              )}
              
              {!result && progress.status === 'idle' && (
                <div className="card text-center">
                  <div className="py-12">
                    <Activity className="h-12 w-12 text-medical-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-medical-900 mb-2">
                      Ready for Analysis
                    </h3>
                    <p className="text-medical-600">
                      Upload a chest CT image to begin NSCLC staging analysis
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-16 text-center text-medical-500">
          <div className="flex items-center justify-center mb-2">
            <Shield className="h-4 w-4 mr-2" />
            <span className="text-sm">
              Secure • HIPAA-Compliant • Research Only
            </span>
          </div>
          <p className="text-xs">
            © 2024 NSCLC Staging Assistant. All rights reserved.
          </p>
        </footer>
      </div>
    </div>
  )
}

export default App 