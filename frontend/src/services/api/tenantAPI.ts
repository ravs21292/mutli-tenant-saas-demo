import { baseAPI } from './base';
import { Tenant, TenantSettings, CreateTenantData, UpdateTenantData } from '../../types/tenant';

export const tenantAPI = {
  getCurrentTenant: async (): Promise<Tenant> => {
    const response = await baseAPI.get<Tenant>('/tenants/');
    return response.data;
  },

  getTenants: async (): Promise<Tenant[]> => {
    const response = await baseAPI.get<Tenant[]>('/tenants/');
    return response.data;
  },

  getSettings: async (): Promise<TenantSettings> => {
    const response = await baseAPI.get<TenantSettings>('/tenants/settings');
    return response.data;
  },

  updateSettings: async (settings: Partial<TenantSettings>): Promise<TenantSettings> => {
    const response = await baseAPI.put<TenantSettings>('/tenants/settings', settings);
    return response.data;
  },

  createTenant: async (tenantData: CreateTenantData): Promise<Tenant> => {
    const response = await baseAPI.post<Tenant>('/tenants/', tenantData);
    return response.data;
  },

  updateTenant: async (tenantId: string, tenantData: UpdateTenantData): Promise<Tenant> => {
    const response = await baseAPI.put<Tenant>(`/tenants/${tenantId}`, tenantData);
    return response.data;
  },

  deleteTenant: async (tenantId: string): Promise<void> => {
    await baseAPI.delete(`/tenants/${tenantId}`);
  },
};
