"""
Project management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user, require_permission
from app.models.user import User
from app.models.project import Project
from app.schemas.project import ProjectResponse, ProjectCreate, ProjectUpdate
from app.services.audit import log_user_action

router = APIRouter()


@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all projects in the current tenant"""
    projects = db.query(Project).filter(Project.tenant_id == current_user.tenant_id).all()
    return projects


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new project"""
    project = Project(
        name=project_data.name,
        description=project_data.description,
        tenant_id=current_user.tenant_id,
        created_by=current_user.id
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Log project creation
    await log_user_action(
        db=db,
        action="create",
        action_type="project.create",
        user=current_user,
        description=f"Project '{project.name}' created",
        target_type="project",
        target_id=project.id
    )
    
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get project by ID"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.tenant_id == current_user.tenant_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.tenant_id == current_user.tenant_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update project fields
    update_data = project_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    
    # Log project update
    await log_user_action(
        db=db,
        action_type="project.update",
        user=current_user,
        description=f"Project '{project.name}' updated",
        resource_type="project",
        resource_id=project.id,
        old_values={},
        new_values=update_data
    )
    
    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.tenant_id == current_user.tenant_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Log project deletion
    await log_user_action(
        db=db,
        action_type="project.delete",
        user=current_user,
        description=f"Project '{project.name}' deleted",
        resource_type="project",
        resource_id=project.id
    )
    
    db.delete(project)
    db.commit()
    
    return {"message": "Project deleted successfully"}
