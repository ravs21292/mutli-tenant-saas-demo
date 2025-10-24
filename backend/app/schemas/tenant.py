"""
Tenant schemas
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class TenantBase(BaseModel):
    """Base tenant schema"""
    name: str
    subdomain: str
    domain: Optional[str] = None


class TenantCreate(TenantBase):
    """Tenant creation schema"""
    subscription_plan: str = "basic"
    settings: Optional[Dict[str, Any]] = None


class TenantUpdate(BaseModel):
    """Tenant update schema"""
    name: Optional[str] = None
    domain: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class TenantResponse(TenantBase):
    """Tenant response schema"""
    id: UUID
    subscription_plan: str
    subscription_status: str
    stripe_customer_id: Optional[str] = None
    max_seats: int
    max_storage_bytes: int
    used_storage_bytes: int
    settings: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TenantSettings(BaseModel):
    """Tenant settings schema"""
    settings: Dict[str, Any]
