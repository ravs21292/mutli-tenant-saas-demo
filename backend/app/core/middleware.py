"""
Custom middleware for tenant isolation and request processing
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging
import uuid

logger = logging.getLogger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware to handle tenant isolation"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """Process request and set tenant context"""
        try:
            # Extract tenant ID from various sources
            tenant_id = await self._extract_tenant_id(request)
            
            if tenant_id:
                # Set tenant context for RLS
                request.state.tenant_id = tenant_id
                
                # Set database session variable for RLS
                # This will be used by the database connection
                request.state.set_tenant_context = True
            else:
                # For public endpoints, allow without tenant context
                if not self._is_public_endpoint(request.url.path):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Tenant ID is required"
                    )
            
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"Tenant middleware error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )
    
    async def _extract_tenant_id(self, request: Request) -> str:
        """Extract tenant ID from request"""
        # Check X-Tenant-ID header
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            try:
                uuid.UUID(tenant_id)
                return tenant_id
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid tenant ID format"
                )
        
        # Check subdomain
        host = request.headers.get("host", "")
        if "." in host:
            subdomain = host.split(".")[0]
            if subdomain and subdomain != "www":
                # Look up tenant by subdomain
                # This would require a database query in a real implementation
                return await self._get_tenant_by_subdomain(subdomain)
        
        # Check JWT token for tenant claim
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            # Decode JWT and extract tenant_id
            # This would require JWT decoding in a real implementation
            return await self._extract_tenant_from_token(token)
        
        return None
    
    async def _get_tenant_by_subdomain(self, subdomain: str) -> str:
        """Get tenant ID by subdomain"""
        # This would query the database in a real implementation
        # For now, return None
        return None
    
    async def _extract_tenant_from_token(self, token: str) -> str:
        """Extract tenant ID from JWT token"""
        # This would decode the JWT in a real implementation
        # For now, return None
        return None
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (doesn't require tenant context)"""
        public_paths = [
            "/",
            "/health",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/webhooks/stripe",
            "/docs",
            "/openapi.json"
        ]
        return any(path.startswith(public_path) for public_path in public_paths)
