"""
Membership model for user-tenant relationships with roles
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime
from enum import Enum


class Role(str, Enum):
    """User roles within a tenant"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class Membership(Base):
    """Membership model for user-tenant relationships with roles"""
    
    __tablename__ = "memberships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    # Role and permissions
    role = Column(String(50), nullable=False, default=Role.MEMBER)
    is_active = Column(Boolean, default=True)
    
    # Invitation
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    invitation_token = Column(String(255), nullable=True)
    invitation_expires_at = Column(DateTime, nullable=True)
    invited_at = Column(DateTime, nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="memberships", foreign_keys=[user_id])
    tenant = relationship("Tenant", back_populates="memberships")
    inviter = relationship("User", foreign_keys=[invited_by])
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'tenant_id', name='unique_user_tenant'),
    )
    
    def __repr__(self):
        return f"<Membership(id={self.id}, user_id={self.user_id}, tenant_id={self.tenant_id}, role={self.role})>"
    
    @property
    def permissions(self):
        """Get permissions based on role"""
        role_permissions = {
            Role.OWNER: [
                "tenant:manage", "user:manage", "project:manage", "file:manage",
                "subscription:manage", "settings:manage", "audit:view"
            ],
            Role.ADMIN: [
                "user:manage", "project:manage", "file:manage", "settings:manage", "audit:view"
            ],
            Role.MEMBER: [
                "project:create", "project:edit", "file:upload", "file:download"
            ],
            Role.VIEWER: [
                "project:view", "file:download"
            ]
        }
        return role_permissions.get(self.role, [])
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        return permission in self.permissions
