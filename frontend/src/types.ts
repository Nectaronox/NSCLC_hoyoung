export interface StagingResult {
  t: string | null;
  n: string | null;
  m: string | null;
  stage: string | null;
  confidences: {
    t: number;
    n: number;
    m: number;
    stage: number;
  };
  error?: string;
}

export interface UploadedFile {
  file: File;
  preview: string;
  name: string;
  size: string;
  type: string;
}

export interface ApiResponse {
  success: boolean;
  data?: StagingResult;
  error?: string;
}

export interface AuthUser {
  id: string;
  username: string;
  role: string;
  token: string;
}

export interface UploadProgress {
  progress: number;
  status: 'idle' | 'uploading' | 'analyzing' | 'completed' | 'error';
  message?: string;
} 