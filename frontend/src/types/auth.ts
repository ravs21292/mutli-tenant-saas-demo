export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  name: string;
  is_active: boolean;
  is_verified: boolean;
  avatar_url?: string;
  timezone: string;
  language: string;
  tenant_id: string;
  created_at: string;
  updated_at: string;
  last_login_at?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  first_name: string;
  last_name: string;
  tenant_name: string;
  subdomain: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthError {
  detail: string;
  errors?: Array<{
    type: string;
    loc: string[];
    msg: string;
    input: any;
    url: string;
  }>;
  error_code?: string;
}