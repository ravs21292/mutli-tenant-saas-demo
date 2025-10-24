"""
User schemas
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    first_name: str
    last_name: str


class UserCreate(UserBase):
    """User creation schema"""
    password: str
    tenant_id: UUID


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""
    id: UUID
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    timezone: str
    language: str
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    """Extended user profile schema"""
    sso_provider: Optional[str] = None
    sso_provider_id: Optional[str] = None
