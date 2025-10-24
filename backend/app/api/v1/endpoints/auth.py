"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import (
    verify_password, get_password_hash, create_access_token, 
    create_refresh_token, verify_token, get_current_user
)
from app.core.config import settings
from app.models.user import User
from app.models.tenant import Tenant
from app.models.membership import Membership
from app.schemas.auth import Token, TokenRefresh, UserLogin, UserRegister, TenantRegister
from app.schemas.user import UserResponse
from app.services.audit import log_action

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return access token"""
    # Find user by email or username
    user = db.query(User).filter(
        (User.email == form_data.username) | (User.username == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "tenant_id": str(user.tenant_id)},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "tenant_id": str(user.tenant_id)}
    )
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # Log login action
    await log_action(
        db=db,
        action="login",
        action_type="user.login",
        actor_user_id=user.id,
        tenant_id=user.tenant_id,
        description="User logged in"
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: TenantRegister,
    db: Session = Depends(get_db)
):
    """Register a new user and create tenant"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Check if tenant subdomain already exists
    existing_tenant = db.query(Tenant).filter(
        Tenant.subdomain == user_data.subdomain
    ).first()
    
    if existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant with this subdomain already exists"
        )
    
    # Create new tenant
    tenant = Tenant(
        name=user_data.tenant_name,
        subdomain=user_data.subdomain
    )
    
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        name=f"{user_data.first_name} {user_data.last_name}",
        tenant_id=tenant.id
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create owner membership
    membership = Membership(
        user_id=user.id,
        tenant_id=tenant.id,
        role="owner"
    )
    
    db.add(membership)
    db.commit()
    
    # Log user creation
    await log_action(
        db=db,
        action="create",
        action_type="user.create",
        actor_user_id=user.id,
        tenant_id=user.tenant_id,
        description="User registered"
    )
    
    return user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    try:
        payload = verify_token(token_data.refresh_token, "refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "tenant_id": str(user.tenant_id)},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "refresh_token": token_data.refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user"""
    # Log logout action
    await log_action(
        db=db,
        action="logout",
        action_type="user.logout",
        actor_user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        description="User logged out"
    )
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user