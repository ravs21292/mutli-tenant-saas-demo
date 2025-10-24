"""
Project schemas
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class ProjectBase(BaseModel):
    """Base project schema"""
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Project creation schema"""
    pass


class ProjectUpdate(BaseModel):
    """Project update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    is_public: Optional[bool] = None
    tags: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


class ProjectResponse(ProjectBase):
    """Project response schema"""
    id: UUID
    status: str
    is_public: bool
    tags: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    tenant_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
