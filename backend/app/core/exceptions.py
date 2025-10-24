"""
Custom exception handlers and error responses
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)


class TenantNotFoundError(Exception):
    """Raised when tenant is not found"""
    pass


class InsufficientPermissionsError(Exception):
    """Raised when user lacks required permissions"""
    pass


class SubscriptionLimitError(Exception):
    """Raised when subscription limits are exceeded"""
    pass


class FileUploadError(Exception):
    """Raised when file upload fails"""
    pass


def setup_exception_handlers(app: FastAPI):
    """Setup custom exception handlers"""
    
    @app.exception_handler(TenantNotFoundError)
    async def tenant_not_found_handler(request: Request, exc: TenantNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": "Tenant not found", "error_code": "TENANT_NOT_FOUND"}
        )
    
    @app.exception_handler(InsufficientPermissionsError)
    async def insufficient_permissions_handler(request: Request, exc: InsufficientPermissionsError):
        return JSONResponse(
            status_code=403,
            content={"detail": "Insufficient permissions", "error_code": "INSUFFICIENT_PERMISSIONS"}
        )
    
    @app.exception_handler(SubscriptionLimitError)
    async def subscription_limit_handler(request: Request, exc: SubscriptionLimitError):
        return JSONResponse(
            status_code=402,
            content={"detail": str(exc), "error_code": "SUBSCRIPTION_LIMIT_EXCEEDED"}
        )
    
    @app.exception_handler(FileUploadError)
    async def file_upload_handler(request: Request, exc: FileUploadError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc), "error_code": "FILE_UPLOAD_ERROR"}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation error",
                "errors": exc.errors(),
                "error_code": "VALIDATION_ERROR"
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_code": "HTTP_ERROR"
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error_code": "INTERNAL_SERVER_ERROR"
            }
        )
