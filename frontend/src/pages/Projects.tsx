import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  Grid,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  SelectChangeEvent,
} from '@mui/material';
import {
  Add,
  MoreVert,
  Edit,
  Delete,
  Folder,
  Public,
  Lock,
} from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '../hooks/redux';
import { fetchProjects, createProject, deleteProject } from '../store/slices/projectSlice';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { CreateProjectData } from '../types/project';

const schema = yup.object({
  name: yup.string().required('Project name is required'),
  description: yup.string().optional(),
  is_public: yup.boolean().optional(),
});

type ProjectFormData = CreateProjectData;

const Projects: React.FC = () => {
  const dispatch = useAppDispatch();
  const { projects, isLoading } = useAppSelector((state) => state.project);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedProject, setSelectedProject] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ProjectFormData>();

  useEffect(() => {
    dispatch(fetchProjects());
  }, [dispatch]);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, projectId: string) => {
    setAnchorEl(event.currentTarget);
    setSelectedProject(projectId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedProject(null);
  };

  const handleDelete = async () => {
    if (selectedProject) {
      await dispatch(deleteProject(selectedProject));
      handleMenuClose();
    }
  };

  const handleCreateProject = async (data: ProjectFormData) => {
    await dispatch(createProject(data));
    setCreateDialogOpen(false);
    reset();
  };

  const handleCreateDialogClose = () => {
    setCreateDialogOpen(false);
    reset();
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Projects</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Create Project
        </Button>
      </Box>

      {isLoading ? (
        <Typography>Loading projects...</Typography>
      ) : (
        <Grid container spacing={3}>
          {projects.map((project) => (
            <Grid item xs={12} sm={6} md={4} key={project.id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                    <Box display="flex" alignItems="center" mb={2}>
                      <Folder color="primary" sx={{ mr: 1 }} />
                      <Typography variant="h6" component="div">
                        {project.name}
                      </Typography>
                    </Box>
                    <IconButton
                      size="small"
                      onClick={(e) => handleMenuOpen(e, project.id)}
                    >
                      <MoreVert />
                    </IconButton>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" mb={2}>
                    {project.description || 'No description'}
                  </Typography>
                  
                  <Box display="flex" gap={1} mb={2}>
                    <Chip
                      label={project.status}
                      color={project.status === 'active' ? 'success' : 'default'}
                      size="small"
                    />
                    {project.is_public ? (
                      <Chip
                        icon={<Public />}
                        label="Public"
                        color="info"
                        size="small"
                      />
                    ) : (
                      <Chip
                        icon={<Lock />}
                        label="Private"
                        color="default"
                        size="small"
                      />
                    )}
                  </Box>
                  
                  <Typography variant="caption" color="text.secondary">
                    Created {new Date(project.created_at).toLocaleDateString()}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button size="small">View Details</Button>
                  <Button size="small">Manage Files</Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
          
          {projects.length === 0 && (
            <Grid item xs={12}>
              <Card>
                <CardContent sx={{ textAlign: 'center', py: 4 }}>
                  <Folder sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No projects yet
                  </Typography>
                  <Typography variant="body2" color="text.secondary" mb={2}>
                    Create your first project to get started with file management
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<Add />}
                    onClick={() => setCreateDialogOpen(true)}
                  >
                    Create Project
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      )}

      {/* Create Project Dialog */}
      <Dialog open={createDialogOpen} onClose={handleCreateDialogClose} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Project</DialogTitle>
        <form onSubmit={handleSubmit(handleCreateProject)}>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Project Name"
              fullWidth
              variant="outlined"
              {...register('name')}
              error={!!errors.name}
              helperText={errors.name?.message}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Description"
              fullWidth
              multiline
              rows={3}
              variant="outlined"
              {...register('description')}
              error={!!errors.description}
              helperText={errors.description?.message}
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth>
              <InputLabel>Visibility</InputLabel>
              <Select
                {...register('is_public')}
                defaultValue={false}
                label="Visibility"
              >
                <MenuItem value="false">Private</MenuItem>
                <MenuItem value="true">Public</MenuItem>
              </Select>
            </FormControl>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCreateDialogClose}>Cancel</Button>
            <Button type="submit" variant="contained">
              Create Project
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Project Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleMenuClose}>
          <Edit sx={{ mr: 1 }} />
          Edit
        </MenuItem>
        <MenuItem onClick={handleDelete}>
          <Delete sx={{ mr: 1 }} />
          Delete
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default Projects;