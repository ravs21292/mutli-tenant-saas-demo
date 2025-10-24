import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { tenantAPI } from '../../services/api/tenantAPI';
import { Tenant, TenantSettings } from '../../types/tenant';

interface TenantState {
  currentTenant: Tenant | null;
  tenants: Tenant[];
  settings: TenantSettings | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: TenantState = {
  currentTenant: null,
  tenants: [],
  settings: null,
  isLoading: false,
  error: null,
};

// Async thunks
export const getCurrentTenant = createAsyncThunk(
  'tenant/getCurrentTenant',
  async (_, { rejectWithValue }) => {
    try {
      const response = await tenantAPI.getCurrentTenant();
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to get tenant');
    }
  }
);

export const getTenantSettings = createAsyncThunk(
  'tenant/getSettings',
  async (_, { rejectWithValue }) => {
    try {
      const response = await tenantAPI.getSettings();
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to get settings');
    }
  }
);

export const updateTenantSettings = createAsyncThunk(
  'tenant/updateSettings',
  async (settings: Partial<TenantSettings>, { rejectWithValue }) => {
    try {
      const response = await tenantAPI.updateSettings(settings);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update settings');
    }
  }
);

const tenantSlice = createSlice({
  name: 'tenant',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setCurrentTenant: (state, action: PayloadAction<Tenant>) => {
      state.currentTenant = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Get current tenant
      .addCase(getCurrentTenant.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(getCurrentTenant.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentTenant = action.payload;
      })
      .addCase(getCurrentTenant.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Get tenant settings
      .addCase(getTenantSettings.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(getTenantSettings.fulfilled, (state, action) => {
        state.isLoading = false;
        state.settings = action.payload;
      })
      .addCase(getTenantSettings.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Update tenant settings
      .addCase(updateTenantSettings.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateTenantSettings.fulfilled, (state, action) => {
        state.isLoading = false;
        state.settings = action.payload;
      })
      .addCase(updateTenantSettings.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError: clearTenantError, setCurrentTenant } = tenantSlice.actions;
export default tenantSlice.reducer;
