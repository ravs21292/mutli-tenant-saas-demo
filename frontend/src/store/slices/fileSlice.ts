import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { fileAPI } from '../../services/api/fileAPI';
import { FileType, UploadFileData } from '../../types/file';

interface FileState {
  files: FileType[];
  currentFile: FileType | null;
  isLoading: boolean;
  isUploading: boolean;
  error: string | null;
  uploadProgress: number;
}

const initialState: FileState = {
  files: [],
  currentFile: null,
  isLoading: false,
  isUploading: false,
  error: null,
  uploadProgress: 0,
};

// Async thunks
export const fetchFiles = createAsyncThunk(
  'file/fetchFiles',
  async (projectId: string, { rejectWithValue }) => {
    try {
      const response = await fileAPI.getFiles(projectId);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch files');
    }
  }
);

export const uploadFile = createAsyncThunk(
  'file/uploadFile',
  async (uploadData: UploadFileData, { rejectWithValue }) => {
    try {
      const response = await fileAPI.uploadFile(uploadData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to upload file');
    }
  }
);

export const getFile = createAsyncThunk(
  'file/getFile',
  async (fileId: string, { rejectWithValue }) => {
    try {
      const response = await fileAPI.getFile(fileId);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to get file');
    }
  }
);

export const downloadFile = createAsyncThunk(
  'file/downloadFile',
  async (fileId: string, { rejectWithValue }) => {
    try {
      const response = await fileAPI.downloadFile(fileId);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to download file');
    }
  }
);

export const deleteFile = createAsyncThunk(
  'file/deleteFile',
  async (fileId: string, { rejectWithValue }) => {
    try {
      await fileAPI.deleteFile(fileId);
      return fileId;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete file');
    }
  }
);

const fileSlice = createSlice({
  name: 'file',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setCurrentFile: (state, action: PayloadAction<FileType | null>) => {
      state.currentFile = action.payload;
    },
    setUploadProgress: (state, action: PayloadAction<number>) => {
      state.uploadProgress = action.payload;
    },
    clearUploadProgress: (state) => {
      state.uploadProgress = 0;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch files
      .addCase(fetchFiles.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchFiles.fulfilled, (state, action) => {
        state.isLoading = false;
        state.files = action.payload;
      })
      .addCase(fetchFiles.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Upload file
      .addCase(uploadFile.pending, (state) => {
        state.isUploading = true;
        state.uploadProgress = 0;
        state.error = null;
      })
      .addCase(uploadFile.fulfilled, (state, action) => {
        state.isUploading = false;
        state.uploadProgress = 100;
        state.files.unshift(action.payload);
      })
      .addCase(uploadFile.rejected, (state, action) => {
        state.isUploading = false;
        state.uploadProgress = 0;
        state.error = action.payload as string;
      })
      // Get file
      .addCase(getFile.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(getFile.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentFile = action.payload;
      })
      .addCase(getFile.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Download file
      .addCase(downloadFile.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(downloadFile.fulfilled, (state) => {
        state.isLoading = false;
      })
      .addCase(downloadFile.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Delete file
      .addCase(deleteFile.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(deleteFile.fulfilled, (state, action) => {
        state.isLoading = false;
        state.files = state.files.filter(f => f.id !== action.payload);
        if (state.currentFile?.id === action.payload) {
          state.currentFile = null;
        }
      })
      .addCase(deleteFile.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { 
  clearError: clearFileError, 
  setCurrentFile, 
  setUploadProgress, 
  clearUploadProgress 
} = fileSlice.actions;
export default fileSlice.reducer;
