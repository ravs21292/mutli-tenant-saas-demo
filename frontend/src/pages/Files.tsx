import React, { useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  LinearProgress,
} from '@mui/material';
import {
  CloudUpload,
  InsertDriveFile,
  Download,
  Delete,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '../hooks/redux';
import { fetchFiles, uploadFile, deleteFile } from '../store/slices/fileSlice';
import { useDropzone } from 'react-dropzone';

const Files: React.FC = () => {
  const dispatch = useAppDispatch();
  const { files, isLoading, isUploading, uploadProgress } = useAppSelector((state) => state.file);
  const { projects } = useAppSelector((state) => state.project);

  useEffect(() => {
    // Fetch files for the first project if available
    if (projects.length > 0) {
      dispatch(fetchFiles(projects[0].id));
    }
  }, [dispatch, projects]);

  const onDrop = async (acceptedFiles: globalThis.File[]) => {
    if (projects.length > 0) {
      for (const file of acceptedFiles) {
        await dispatch(uploadFile({
          file,
          project_id: projects[0].id,
          is_public: false,
          access_level: 'private',
        }));
      }
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    disabled: projects.length === 0,
  });

  const handleDownload = (fileId: string) => {
    // TODO: Implement file download
    console.log('Download file:', fileId);
  };

  const handleDelete = async (fileId: string) => {
    await dispatch(deleteFile(fileId));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (mimeType: string) => {
    if (mimeType.startsWith('image/')) return '🖼️';
    if (mimeType.startsWith('video/')) return '🎥';
    if (mimeType.startsWith('audio/')) return '🎵';
    if (mimeType.includes('pdf')) return '📄';
    if (mimeType.includes('word')) return '📝';
    if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) return '📊';
    return '📁';
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Files
      </Typography>

      {projects.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <InsertDriveFile sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No projects available
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={2}>
              Create a project first to start uploading files
            </Typography>
            <Button variant="contained" href="/projects">
              Go to Projects
            </Button>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Upload Area */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box
                {...getRootProps()}
                sx={{
                  border: '2px dashed',
                  borderColor: isDragActive ? 'primary.main' : 'grey.300',
                  borderRadius: 2,
                  p: 4,
                  textAlign: 'center',
                  cursor: 'pointer',
                  bgcolor: isDragActive ? 'action.hover' : 'transparent',
                  transition: 'all 0.2s ease-in-out',
                }}
              >
                <input {...getInputProps()} />
                <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  {isDragActive ? 'Drop files here' : 'Drag & drop files here, or click to select'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Support for all file types
                </Typography>
                {isUploading && (
                  <Box sx={{ mt: 2 }}>
                    <LinearProgress variant="determinate" value={uploadProgress} />
                    <Typography variant="caption" color="text.secondary">
                      Uploading... {uploadProgress}%
                    </Typography>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>

          {/* Files List */}
          {isLoading ? (
            <Typography>Loading files...</Typography>
          ) : (
            <Grid container spacing={2}>
              {files.map((file) => (
                <Grid item xs={12} sm={6} md={4} lg={3} key={file.id}>
                  <Card>
                    <CardContent>
                      <Box display="flex" alignItems="center" mb={2}>
                        <Typography variant="h4" sx={{ mr: 2 }}>
                          {getFileIcon(file.mime_type)}
                        </Typography>
                        <Box flexGrow={1}>
                          <Typography variant="subtitle1" noWrap>
                            {file.original_filename}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {formatFileSize(file.size)}
                          </Typography>
                        </Box>
                      </Box>
                      
                      <Box display="flex" gap={1} mb={2}>
                        <Chip
                          label={file.access_level}
                          color={file.access_level === 'public' ? 'success' : 'default'}
                          size="small"
                        />
                        {file.is_public ? (
                          <Chip
                            icon={<Visibility />}
                            label="Public"
                            color="info"
                            size="small"
                          />
                        ) : (
                          <Chip
                            icon={<VisibilityOff />}
                            label="Private"
                            color="default"
                            size="small"
                          />
                        )}
                      </Box>
                      
                      <Typography variant="caption" color="text.secondary">
                        Uploaded {new Date(file.created_at).toLocaleDateString()}
                      </Typography>
                    </CardContent>
                    <Box display="flex" justifyContent="space-between" p={2}>
                      <Button
                        size="small"
                        startIcon={<Download />}
                        onClick={() => handleDownload(file.id)}
                      >
                        Download
                      </Button>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDelete(file.id)}
                      >
                        <Delete />
                      </IconButton>
                    </Box>
                  </Card>
                </Grid>
              ))}
              
              {files.length === 0 && (
                <Grid item xs={12}>
                  <Card>
                    <CardContent sx={{ textAlign: 'center', py: 4 }}>
                      <InsertDriveFile sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                      <Typography variant="h6" color="text.secondary" gutterBottom>
                        No files uploaded yet
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Drag and drop files above to get started
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              )}
            </Grid>
          )}
        </>
      )}
    </Box>
  );
};

export default Files;