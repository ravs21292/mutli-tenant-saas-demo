"""
File schemas
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class FileBase(BaseModel):
    """Base file schema"""
    filename: str
    original_filename: str
    size: int
    mime: str


class FileUpload(BaseModel):
    """File upload schema"""
    project_id: Optional[str] = None


class FileResponse(FileBase):
    """File response schema"""
    id: UUID
    s3_key: str
    file_url: Optional[str] = None
    file_hash: Optional[str] = None
    is_public: bool
    access_level: str
    tenant_id: UUID
    project_id: Optional[UUID] = None
    uploaded_by: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
