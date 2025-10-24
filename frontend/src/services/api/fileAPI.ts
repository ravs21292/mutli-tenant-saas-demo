import { baseAPI } from './base';
import { FileType, UploadFileData, FileFilter, FileUploadResponse } from '../../types/file';

export const fileAPI = {
  getFiles: async (projectId: string, filters?: FileFilter): Promise<FileType[]> => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    
    const response = await baseAPI.get<FileType[]>(`/files/?project_id=${projectId}&${params.toString()}`);
    return response.data;
  },

  getFile: async (fileId: string): Promise<FileType> => {
    const response = await baseAPI.get<FileType>(`/files/${fileId}`);
    return response.data;
  },

  uploadFile: async (uploadData: UploadFileData, onUploadProgress?: (progressEvent: any) => void): Promise<FileType> => {
    const formData = new FormData();
    formData.append('file', uploadData.file);
    formData.append('project_id', uploadData.project_id);
    
    if (uploadData.is_public !== undefined) {
      formData.append('is_public', uploadData.is_public.toString());
    }
    
    if (uploadData.access_level) {
      formData.append('access_level', uploadData.access_level);
    }

    const response = await baseAPI.upload<FileType>('/files/upload', formData, onUploadProgress);
    return response.data;
  },

  downloadFile: async (fileId: string): Promise<FileUploadResponse> => {
    const response = await baseAPI.get<FileUploadResponse>(`/files/${fileId}/download`);
    return response.data;
  },

  deleteFile: async (fileId: string): Promise<void> => {
    await baseAPI.delete(`/files/${fileId}`);
  },

  getFileUrl: (fileId: string): string => {
    return `${process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1'}/files/${fileId}/download`;
  },
};
