"""
File storage service for S3 integration
"""

import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
from typing import Optional, BinaryIO
import logging

logger = logging.getLogger(__name__)


class FileStorageService:
    """Service for file storage operations"""
    
    def __init__(self):
        self.s3_client = None
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
    
    async def upload_file(
        self,
        file_obj: BinaryIO,
        bucket_name: str,
        key: str,
        content_type: str,
        metadata: Optional[dict] = None
    ) -> str:
        """Upload file to S3"""
        if not self.s3_client:
            raise Exception("S3 client not configured")
        
        try:
            extra_args = {
                'ContentType': content_type
            }
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.s3_client.upload_fileobj(
                file_obj,
                bucket_name,
                key,
                ExtraArgs=extra_args
            )
            
            # Generate presigned URL for access
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': key},
                ExpiresIn=3600  # 1 hour
            )
            
            return url
            
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {e}")
            raise Exception(f"Failed to upload file: {e}")
    
    async def delete_file(self, bucket_name: str, key: str) -> bool:
        """Delete file from S3"""
        if not self.s3_client:
            raise Exception("S3 client not configured")
        
        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=key)
            return True
        except ClientError as e:
            logger.error(f"Error deleting file from S3: {e}")
            return False
    
    async def generate_presigned_url(
        self,
        bucket_name: str,
        key: str,
        expiration: int = 3600
    ) -> str:
        """Generate presigned URL for file access"""
        if not self.s3_client:
            raise Exception("S3 client not configured")
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise Exception(f"Failed to generate presigned URL: {e}")
    
    async def get_file_metadata(self, bucket_name: str, key: str) -> dict:
        """Get file metadata from S3"""
        if not self.s3_client:
            raise Exception("S3 client not configured")
        
        try:
            response = self.s3_client.head_object(Bucket=bucket_name, Key=key)
            return {
                'size': response['ContentLength'],
                'content_type': response['ContentType'],
                'last_modified': response['LastModified'],
                'etag': response['ETag']
            }
        except ClientError as e:
            logger.error(f"Error getting file metadata: {e}")
            raise Exception(f"Failed to get file metadata: {e}")


# Global file storage service instance
file_storage = FileStorageService()
