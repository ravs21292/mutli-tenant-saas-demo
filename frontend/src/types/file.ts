export interface FileType {
  id: string;
  name: string;
  original_filename: string;
  s3_key: string;
  file_url: string;
  file_hash: string;
  size: number;
  mime_type: string;
  is_public: boolean;
  access_level: 'private' | 'team' | 'public';
  tenant_id: string;
  project_id: string;
  uploaded_by: string;
  created_at: string;
  updated_at: string;
}

export interface UploadFileData {
  file: globalThis.File;
  project_id: string;
  is_public?: boolean;
  access_level?: 'private' | 'team' | 'public';
}

export interface FileUploadProgress {
  fileId: string;
  progress: number;
  status: 'uploading' | 'completed' | 'error';
  error?: string;
}

export interface FileFilter {
  project_id?: string;
  mime_type?: string;
  is_public?: boolean;
  access_level?: 'private' | 'team' | 'public';
  uploaded_by?: string;
  date_from?: string;
  date_to?: string;
  search?: string;
}

export interface FileUploadResponse {
  download_url: string;
}
