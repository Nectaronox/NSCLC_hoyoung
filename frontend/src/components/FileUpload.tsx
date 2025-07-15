import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileImage, AlertCircle } from 'lucide-react'
import { UploadedFile } from '../types'
import toast from 'react-hot-toast'

interface FileUploadProps {
  onFileUpload: (file: UploadedFile) => void
  uploadedFile: UploadedFile | null
  isProcessing: boolean
}

export const FileUpload: React.FC<FileUploadProps> = ({ 
  onFileUpload, 
  uploadedFile, 
  isProcessing 
}) => {
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const validateFile = (file: File): boolean => {
    // Check file type
    const allowedTypes = [
      'image/jpeg',
      'image/png',
      'image/jpg',
      'application/dicom',
      'application/octet-stream' // DICOM files might have this MIME type
    ]
    
    const allowedExtensions = ['.dcm', '.png', '.jpg', '.jpeg']
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
      toast.error('Please upload a valid CT image file (.dcm, .png, .jpg)')
      return false
    }

    // Check file size (max 50MB)
    if (file.size > 50 * 1024 * 1024) {
      toast.error('File size must be less than 50MB')
      return false
    }

    return true
  }

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return
    
    const file = acceptedFiles[0]
    if (!validateFile(file)) return

    // Create preview URL only for image files
    const preview = file.type.startsWith('image/') ? URL.createObjectURL(file) : ''
    
    const uploadedFile: UploadedFile = {
      file,
      preview,
      name: file.name,
      size: formatFileSize(file.size),
      type: file.type || 'application/octet-stream'
    }

    onFileUpload(uploadedFile)
  }, [onFileUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'application/dicom': ['.dcm'],
      'application/octet-stream': ['.dcm']
    },
    maxFiles: 1,
    multiple: false,
    disabled: isProcessing
  })

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4 text-medical-900">
        Upload CT Image
      </h2>
      
      <div 
        {...getRootProps()} 
        className={`upload-zone ${isDragActive ? 'drag-active' : ''} ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-4">
          <div className="p-4 bg-primary-100 rounded-full">
            <Upload className="h-8 w-8 text-primary-600" />
          </div>
          
          <div className="text-center">
            <p className="text-lg font-medium text-medical-900 mb-2">
              {isDragActive ? 'Drop the file here' : 'Drag & drop your CT image'}
            </p>
            <p className="text-medical-600 mb-4">
              or <span className="text-primary-600 font-medium">browse files</span>
            </p>
            
            <div className="bg-medical-100 rounded-lg p-3 text-sm text-medical-700">
              <div className="flex items-center justify-center mb-2">
                <FileImage className="h-4 w-4 mr-2" />
                <span className="font-medium">Supported formats:</span>
              </div>
              <p>DICOM (.dcm), PNG (.png), JPEG (.jpg)</p>
              <p className="text-xs mt-1">Maximum file size: 50MB</p>
            </div>
          </div>
        </div>
      </div>

      {isProcessing && (
        <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-3"></div>
            <span className="text-blue-800">Processing your CT image...</span>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="mt-6 bg-medical-50 border border-medical-200 rounded-lg p-4">
        <div className="flex items-start">
          <AlertCircle className="h-5 w-5 text-medical-600 mt-0.5 mr-2 flex-shrink-0" />
          <div className="text-medical-700 text-sm">
            <p className="font-medium mb-2">Image Guidelines:</p>
            <ul className="space-y-1 text-xs">
              <li>• High-resolution chest CT scans preferred</li>
              <li>• Axial, coronal, or sagittal views accepted</li>
              <li>• Clear visualization of lung parenchyma required</li>
              <li>• DICOM format recommended for best results</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Show uploaded file info */}
      {uploadedFile && (
        <div className="mt-4 bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <FileImage className="h-5 w-5 text-green-600 mr-3" />
              <div>
                <p className="font-medium text-green-800">{uploadedFile.name}</p>
                <p className="text-sm text-green-600">
                  {uploadedFile.size} • {uploadedFile.type}
                </p>
              </div>
            </div>
            {uploadedFile.preview && (
              <img 
                src={uploadedFile.preview} 
                alt="Preview" 
                className="h-12 w-12 object-cover rounded border"
              />
            )}
          </div>
        </div>
      )}
    </div>
  )
} 