"""
File management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user, require_permission
from app.models.user import User
from app.models.file import File as FileModel
from app.models.project import Project
from app.schemas.file import FileResponse, FileUpload
from app.services.audit import log_user_action
from app.services.file_storage import file_storage
from app.core.config import settings
import uuid
import hashlib

router = APIRouter()


@router.get("/", response_model=List[FileResponse])
async def get_files(
    project_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all files in the current tenant"""
    query = db.query(FileModel).filter(FileModel.tenant_id == current_user.tenant_id)
    
    if project_id:
        query = query.filter(FileModel.project_id == project_id)
    
    files = query.all()
    return files


@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    project_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a new file"""
    # Validate file type
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not allowed"
        )
    
    # Validate file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum allowed size"
        )
    
    # Check storage limits
    tenant = current_user.tenant
    if tenant.used_storage_bytes + len(file_content) > tenant.max_storage_bytes:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Storage limit exceeded"
        )
    
    # Generate file hash for deduplication
    file_hash = hashlib.sha256(file_content).hexdigest()
    
    # Check if file already exists
    existing_file = db.query(FileModel).filter(
        FileModel.file_hash == file_hash,
        FileModel.tenant_id == current_user.tenant_id
    ).first()
    
    if existing_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File already exists"
        )
    
    # Generate S3 key
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
    s3_key = f"tenants/{current_user.tenant_id}/files/{uuid.uuid4()}.{file_extension}"
    
    # Upload to S3
    try:
        file_url = await file_storage.upload_file(
            file_obj=file_content,
            bucket_name=settings.S3_BUCKET_NAME,
            key=s3_key,
            content_type=file.content_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )
    
    # Create file record
    file_record = FileModel(
        filename=file.filename,
        original_filename=file.filename,
        s3_key=s3_key,
        file_url=file_url,
        size=len(file_content),
        mime=file.content_type,
        file_hash=file_hash,
        tenant_id=current_user.tenant_id,
        project_id=project_id,
        uploaded_by=current_user.id
    )
    
    db.add(file_record)
    
    # Update tenant storage usage
    tenant.used_storage_bytes += len(file_content)
    
    db.commit()
    db.refresh(file_record)
    
    # Log file upload
    await log_user_action(
        db=db,
        action_type="file.upload",
        user=current_user,
        description=f"File '{file.filename}' uploaded",
        resource_type="file",
        resource_id=file_record.id,
        metadata={
            "filename": file.filename,
            "file_size": len(file_content),
            "mime_type": file.content_type
        }
    )
    
    return file_record


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get file by ID"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.tenant_id == current_user.tenant_id
    ).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return file


@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get download URL for file"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.tenant_id == current_user.tenant_id
    ).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Generate presigned URL
    try:
        download_url = await file_storage.generate_presigned_url(
            bucket_name=settings.S3_BUCKET_NAME,
            key=file.s3_key,
            expiration=3600  # 1 hour
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate download URL: {str(e)}"
        )
    
    # Log file download
    await log_user_action(
        db=db,
        action_type="file.download",
        user=current_user,
        description=f"File '{file.filename}' downloaded",
        resource_type="file",
        resource_id=file.id
    )
    
    return {"download_url": download_url}


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete file"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.tenant_id == current_user.tenant_id
    ).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Delete from S3
    try:
        await file_storage.delete_file(
            bucket_name=settings.S3_BUCKET_NAME,
            key=file.s3_key
        )
    except Exception as e:
        # Log error but continue with database deletion
        pass
    
    # Update tenant storage usage
    tenant = current_user.tenant
    tenant.used_storage_bytes -= file.size
    
    # Log file deletion
    await log_user_action(
        db=db,
        action_type="file.delete",
        user=current_user,
        description=f"File '{file.filename}' deleted",
        resource_type="file",
        resource_id=file.id
    )
    
    db.delete(file)
    db.commit()
    
    return {"message": "File deleted successfully"}
