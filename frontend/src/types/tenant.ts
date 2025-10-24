export interface Tenant {
  id: string;
  name: string;
  subdomain: string;
  domain?: string;
  plan: 'basic' | 'pro' | 'enterprise';
  storage_quota_bytes: number;
  settings?: TenantSettings;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TenantSettings {
  allow_registration: boolean;
  require_email_verification: boolean;
  default_user_role: 'admin' | 'member' | 'viewer';
  max_users: number;
  features: {
    file_upload: boolean;
    project_management: boolean;
    team_collaboration: boolean;
    advanced_analytics: boolean;
  };
  branding: {
    logo_url?: string;
    primary_color?: string;
    secondary_color?: string;
  };
  notifications: {
    email_notifications: boolean;
    slack_integration: boolean;
    webhook_url?: string;
  };
}

export interface CreateTenantData {
  name: string;
  subdomain: string;
  domain?: string;
  plan?: 'basic' | 'pro' | 'enterprise';
}

export interface UpdateTenantData {
  name?: string;
  domain?: string;
  settings?: Partial<TenantSettings>;
}