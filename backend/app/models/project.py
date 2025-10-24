"""
Project model for tenant projects
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime


class Project(Base):
    """Project model for tenant projects"""
    
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Status and settings
    status = Column(String(50), default="active")  # active, archived, deleted, completed
    is_public = Column(Boolean, default=False)
    
    # Metadata
    tags = Column(JSON, nullable=True)  # JSON for tags
    settings = Column(JSON, nullable=True)  # JSON for project settings
    
    # Foreign keys
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="projects")
    created_by_user = relationship("User", back_populates="created_projects")
    files = relationship("File", back_populates="project")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, tenant_id={self.tenant_id})>"
