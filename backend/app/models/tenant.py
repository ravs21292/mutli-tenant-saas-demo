"""
Tenant model for multi-tenancy
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime


class Tenant(Base):
    """Tenant model for multi-tenant isolation"""
    
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    subdomain = Column(String(100), unique=True, nullable=False)
    domain = Column(String(255), unique=True, nullable=True)
    
    # Subscription information (legacy - now handled by subscription table)
    plan = Column(String(50), default="basic")  # basic, pro, enterprise
    storage_quota_bytes = Column(Integer, default=1073741824)  # 1GB default
    
    # Settings
    settings = Column(JSON, nullable=True)  # JSON for tenant-specific settings
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    memberships = relationship("Membership", back_populates="tenant")
    projects = relationship("Project", back_populates="tenant")
    files = relationship("File", back_populates="tenant")
    audit_logs = relationship("AuditLog", back_populates="tenant")
    billing_customer = relationship("BillingCustomer", back_populates="tenant", uselist=False)
    subscription = relationship("Subscription", back_populates="tenant", uselist=False)
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, name={self.name}, subdomain={self.subdomain})>"
