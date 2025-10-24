import { baseAPI } from './base';
import { User, LoginCredentials, RegisterData, TokenResponse } from '../../types/auth';

export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<TokenResponse> => {
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await baseAPI.post<TokenResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  register: async (userData: RegisterData): Promise<User> => {
    const response = await baseAPI.post<User>('/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await baseAPI.get<User>('/auth/me');
    return response.data;
  },

  refreshToken: async (): Promise<TokenResponse> => {
    const state = require('../../store').store.getState();
    const refreshToken = state.auth.refreshToken;

    const response = await baseAPI.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  logout: async (): Promise<void> => {
    await baseAPI.post('/auth/logout');
  },
};
