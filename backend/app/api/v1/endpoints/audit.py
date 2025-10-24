"""
Audit log endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import get_current_user, require_permission
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.audit import AuditLogResponse, AuditLogFilter

router = APIRouter()


@router.get("/", response_model=List[AuditLogResponse])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    action_type: Optional[str] = None,
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit logs for the current tenant"""
    # Build query
    query = db.query(AuditLog).filter(AuditLog.tenant_id == current_user.tenant_id)
    
    # Apply filters
    if action_type:
        query = query.filter(AuditLog.action_type == action_type)
    
    if user_id:
        query = query.filter(AuditLog.actor_user_id == user_id)
    
    if resource_type:
        query = query.filter(AuditLog.target_type == resource_type)
    
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    # Order by created_at descending
    query = query.order_by(AuditLog.created_at.desc())
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    audit_logs = query.all()
    return audit_logs


@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific audit log by ID"""
    audit_log = db.query(AuditLog).filter(
        AuditLog.id == log_id,
        AuditLog.tenant_id == current_user.tenant_id
    ).first()
    
    if not audit_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )
    
    return audit_log


@router.get("/stats/summary")
async def get_audit_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit log statistics summary"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get total actions
    total_actions = db.query(AuditLog).filter(
        AuditLog.tenant_id == current_user.tenant_id,
        AuditLog.created_at >= start_date
    ).count()
    
    # Get actions by type
    actions_by_type = db.query(
        AuditLog.action_type,
        db.func.count(AuditLog.id).label('count')
    ).filter(
        AuditLog.tenant_id == current_user.tenant_id,
        AuditLog.created_at >= start_date
    ).group_by(AuditLog.action_type).all()
    
    # Get actions by user
    actions_by_user = db.query(
        AuditLog.actor_user_id,
        db.func.count(AuditLog.id).label('count')
    ).filter(
        AuditLog.tenant_id == current_user.tenant_id,
        AuditLog.created_at >= start_date,
        AuditLog.actor_user_id.isnot(None)
    ).group_by(AuditLog.actor_user_id).all()
    
    return {
        "total_actions": total_actions,
        "actions_by_type": [{"action_type": item[0], "count": item[1]} for item in actions_by_type],
        "actions_by_user": [{"user_id": str(item[0]), "count": item[1]} for item in actions_by_user],
        "period_days": days
    }
