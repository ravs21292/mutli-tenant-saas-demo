"""
Authentication schemas
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str
    tenant_id: UUID


class TenantRegister(BaseModel):
    """Tenant registration schema"""
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str
    tenant_name: str
    subdomain: str


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class TokenRefresh(BaseModel):
    """Token refresh schema"""
    refresh_token: str


class PasswordReset(BaseModel):
    """Password reset schema"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str
    new_password: str
