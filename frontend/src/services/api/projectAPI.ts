import { baseAPI } from './base';
import { Project, CreateProjectData, UpdateProjectData, ProjectStats } from '../../types/project';

export const projectAPI = {
  getProjects: async (): Promise<Project[]> => {
    const response = await baseAPI.get<Project[]>('/projects/');
    return response.data;
  },

  getProject: async (projectId: string): Promise<Project> => {
    const response = await baseAPI.get<Project>(`/projects/${projectId}`);
    return response.data;
  },

  createProject: async (projectData: CreateProjectData): Promise<Project> => {
    const response = await baseAPI.post<Project>('/projects/', projectData);
    return response.data;
  },

  updateProject: async (projectId: string, projectData: UpdateProjectData): Promise<Project> => {
    const response = await baseAPI.put<Project>(`/projects/${projectId}`, projectData);
    return response.data;
  },

  deleteProject: async (projectId: string): Promise<void> => {
    await baseAPI.delete(`/projects/${projectId}`);
  },

  getProjectStats: async (projectId: string): Promise<ProjectStats> => {
    const response = await baseAPI.get<ProjectStats>(`/projects/${projectId}/stats`);
    return response.data;
  },
};
