"""
Audit log schemas
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class AuditLogResponse(BaseModel):
    """Audit log response schema"""
    id: UUID
    action: str
    action_type: str
    action_description: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[UUID] = None
    actor_user_id: Optional[UUID] = None
    tenant_id: UUID
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogFilter(BaseModel):
    """Audit log filter schema"""
    action_type: Optional[str] = None
    actor_user_id: Optional[UUID] = None
    target_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = 0
    limit: int = 100
