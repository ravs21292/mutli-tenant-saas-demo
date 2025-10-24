"""
Audit log model for tracking user actions and system events
"""

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime
from enum import Enum


class ActionType(str, Enum):
    """Types of actions that can be logged"""
    # User actions
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_CREATE = "user.create"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"
    
    # Tenant actions
    TENANT_CREATE = "tenant.create"
    TENANT_UPDATE = "tenant.update"
    TENANT_DELETE = "tenant.delete"
    
    # Project actions
    PROJECT_CREATE = "project.create"
    PROJECT_UPDATE = "project.update"
    PROJECT_DELETE = "project.delete"
    
    # File actions
    FILE_UPLOAD = "file.upload"
    FILE_DOWNLOAD = "file.download"
    FILE_DELETE = "file.delete"
    
    # Membership actions
    MEMBERSHIP_CREATE = "membership.create"
    MEMBERSHIP_UPDATE = "membership.update"
    MEMBERSHIP_DELETE = "membership.delete"
    
    # Subscription actions
    SUBSCRIPTION_CREATE = "subscription.create"
    SUBSCRIPTION_UPDATE = "subscription.update"
    SUBSCRIPTION_CANCEL = "subscription.cancel"
    
    # System actions
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"


class AuditLog(Base):
    """Audit log model for tracking actions and events"""
    
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Action details
    action = Column(String(100), nullable=False)  # action performed
    action_type = Column(String(100), nullable=False)  # type of action
    action_description = Column(Text, nullable=True)
    
    # Context
    target_type = Column(String(100), nullable=True)  # user, project, file, etc.
    target_id = Column(UUID(as_uuid=True), nullable=True)
    
    # User and tenant context
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    # Request context
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(255), nullable=True)
    
    # Additional data
    meta = Column(JSON, nullable=True)  # Additional context data
    old_values = Column(JSON, nullable=True)  # For update actions
    new_values = Column(JSON, nullable=True)  # For create/update actions
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    tenant = relationship("Tenant", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, actor_user_id={self.actor_user_id})>"
