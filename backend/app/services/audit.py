"""
Audit logging service
"""

from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog, ActionType
from app.models.user import User
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


async def log_action(
    db: Session,
    action: str,
    action_type: str,
    actor_user_id: Optional[UUID] = None,
    tenant_id: Optional[UUID] = None,
    target_type: Optional[str] = None,
    target_id: Optional[UUID] = None,
    description: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_id: Optional[str] = None
) -> AuditLog:
    """Log an action to the audit log"""
    
    audit_log = AuditLog(
        action=action,
        action_type=action_type,
        action_description=description,
        target_type=target_type,
        target_id=target_id,
        actor_user_id=actor_user_id,
        tenant_id=tenant_id,
        ip_address=ip_address,
        user_agent=user_agent,
        request_id=request_id,
        meta=meta,
        old_values=old_values,
        new_values=new_values
    )
    
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    
    return audit_log


async def log_user_action(
    db: Session,
    action: str,
    action_type: str,
    user: User,
    description: Optional[str] = None,
    target_type: Optional[str] = None,
    target_id: Optional[UUID] = None,
    meta: Optional[Dict[str, Any]] = None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """Log a user action with user context"""
    
    return await log_action(
        db=db,
        action=action,
        action_type=action_type,
        actor_user_id=user.id,
        tenant_id=user.tenant_id,
        target_type=target_type,
        target_id=target_id,
        description=description,
        meta=meta,
        old_values=old_values,
        new_values=new_values
    )


async def log_system_event(
    db: Session,
    action: str,
    action_type: str,
    tenant_id: Optional[UUID] = None,
    description: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """Log a system event"""
    
    return await log_action(
        db=db,
        action=action,
        action_type=action_type,
        tenant_id=tenant_id,
        description=description,
        meta=meta
    )
