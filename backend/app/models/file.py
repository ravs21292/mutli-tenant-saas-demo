"""
File model for file uploads and management
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime


class File(Base):
    """File model for file uploads and management"""
    
    __tablename__ = "files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    s3_key = Column(String(500), nullable=False)  # S3 key for file storage
    file_url = Column(String(500), nullable=True)  # Public URL for access
    
    # File metadata
    size = Column(BigInteger, nullable=False)  # File size in bytes
    mime = Column(String(100), nullable=False)  # MIME type
    file_hash = Column(String(64), nullable=True)  # SHA-256 hash for deduplication
    
    # Access control
    is_public = Column(Boolean, default=False)
    access_level = Column(String(50), default="private")  # private, tenant, public
    
    # Foreign keys
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="files")
    project = relationship("Project", back_populates="files")
    uploaded_by_user = relationship("User", back_populates="uploaded_files")
    
    def __repr__(self):
        return f"<File(id={self.id}, filename={self.filename}, size={self.size})>"
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in MB"""
        return self.size / (1024 * 1024)
    
    @property
    def file_extension(self) -> str:
        """Get file extension"""
        return self.original_filename.split('.')[-1].lower() if '.' in self.original_filename else ''
