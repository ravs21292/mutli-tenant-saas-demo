import React, { useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Avatar,
} from '@mui/material';
import {
  Folder,
  CloudUpload,
  People,
  Assessment,
  TrendingUp,
  RecentActors,
} from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '../hooks/redux';
import { fetchProjects } from '../store/slices/projectSlice';
import { getCurrentTenant } from '../store/slices/tenantSlice';

const Dashboard: React.FC = () => {
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);
  const { currentTenant } = useAppSelector((state) => state.tenant);
  const { projects, isLoading } = useAppSelector((state) => state.project);

  useEffect(() => {
    dispatch(fetchProjects());
    dispatch(getCurrentTenant());
  }, [dispatch]);

  const recentProjects = projects.slice(0, 5);
  const totalFiles = projects.reduce((acc, project) => acc + (project as any).file_count || 0, 0);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Welcome back, {user?.first_name}!
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        {currentTenant?.name} • {currentTenant?.plan?.toUpperCase()} Plan
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Stats Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                  <Folder />
                </Avatar>
                <Box>
                  <Typography variant="h6">{projects.length}</Typography>
                  <Typography color="text.secondary">Projects</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Avatar sx={{ bgcolor: 'secondary.main', mr: 2 }}>
                  <CloudUpload />
                </Avatar>
                <Box>
                  <Typography variant="h6">{totalFiles}</Typography>
                  <Typography color="text.secondary">Files</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
                  <People />
                </Avatar>
                <Box>
                  <Typography variant="h6">1</Typography>
                  <Typography color="text.secondary">Team Members</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Avatar sx={{ bgcolor: 'warning.main', mr: 2 }}>
                  <TrendingUp />
                </Avatar>
                <Box>
                  <Typography variant="h6">0</Typography>
                  <Typography color="text.secondary">Storage Used</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Projects */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Projects
            </Typography>
            <List>
              {recentProjects.map((project) => (
                <ListItem key={project.id} divider>
                  <ListItemIcon>
                    <Folder color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary={project.name}
                    secondary={project.description || 'No description'}
                  />
                  <Chip
                    label={project.status}
                    color={project.status === 'active' ? 'success' : 'default'}
                    size="small"
                  />
                </ListItem>
              ))}
              {projects.length === 0 && (
                <ListItem>
                  <ListItemText
                    primary="No projects yet"
                    secondary="Create your first project to get started"
                  />
                </ListItem>
              )}
            </List>
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <List>
              <ListItem button>
                <ListItemIcon>
                  <Folder />
                </ListItemIcon>
                <ListItemText primary="Create Project" />
              </ListItem>
              <ListItem button>
                <ListItemIcon>
                  <CloudUpload />
                </ListItemIcon>
                <ListItemText primary="Upload Files" />
              </ListItem>
              <ListItem button>
                <ListItemIcon>
                  <People />
                </ListItemIcon>
                <ListItemText primary="Invite Team" />
              </ListItem>
              <ListItem button>
                <ListItemIcon>
                  <Assessment />
                </ListItemIcon>
                <ListItemText primary="View Reports" />
              </ListItem>
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;