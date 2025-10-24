"""
Tenant management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user, require_owner
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.tenant import TenantResponse, TenantUpdate, TenantSettings
from app.services.audit import log_user_action

router = APIRouter()


@router.get("/", response_model=TenantResponse)
async def get_current_tenant(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current tenant information"""
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    return tenant


@router.put("/", response_model=TenantResponse)
async def update_tenant(
    tenant_update: TenantUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update tenant information"""
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Update tenant fields
    update_data = tenant_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)
    
    db.commit()
    db.refresh(tenant)
    
    # Log tenant update
    await log_user_action(
        db=db,
        action_type="tenant.update",
        user=current_user,
        description="Tenant information updated",
        old_values={"name": tenant.name, "domain": tenant.domain},
        new_values=update_data
    )
    
    return tenant


@router.put("/settings", response_model=TenantSettings)
async def update_tenant_settings(
    settings: TenantSettings,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update tenant settings"""
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Update settings
    tenant.settings = settings.settings
    db.commit()
    
    # Log settings update
    await log_user_action(
        db=db,
        action_type="tenant.update",
        user=current_user,
        description="Tenant settings updated",
        metadata={"settings": settings.settings}
    )
    
    return settings
