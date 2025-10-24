export interface Project {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'inactive' | 'archived';
  is_public: boolean;
  tags?: string[];
  settings?: ProjectSettings;
  tenant_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectSettings {
  allow_public_access: boolean;
  require_approval: boolean;
  auto_archive_days?: number;
  notifications: {
    on_file_upload: boolean;
    on_file_download: boolean;
    on_member_join: boolean;
  };
  permissions: {
    allow_member_upload: boolean;
    allow_member_download: boolean;
    allow_member_comment: boolean;
  };
}

export interface CreateProjectData {
  name: string;
  description?: string | undefined;
  is_public?: boolean | undefined;
  tags?: string[];
  settings?: Partial<ProjectSettings>;
}

export interface UpdateProjectData {
  name?: string;
  description?: string;
  status?: 'active' | 'inactive' | 'archived';
  is_public?: boolean;
  tags?: string[];
  settings?: Partial<ProjectSettings>;
}

export interface ProjectStats {
  total_files: number;
  total_size: number;
  total_members: number;
  last_activity: string;
}