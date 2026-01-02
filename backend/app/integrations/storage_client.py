"""
Storage client for object storage (S3-compatible).
"""
import uuid
from typing import BinaryIO
from datetime import datetime

from app.config import settings


class StorageClient:
    """
    Client for object storage operations.
    Supports S3-compatible storage backends.
    """
    
    def __init__(self):
        self.bucket = settings.STORAGE_BUCKET
        self._client = None
    
    def _get_client(self):
        """Lazy initialization of S3 client."""
        if self._client is None:
            import boto3
            
            client_kwargs = {
                "service_name": "s3",
            }
            
            if settings.STORAGE_ENDPOINT:
                client_kwargs["endpoint_url"] = settings.STORAGE_ENDPOINT
            if settings.STORAGE_ACCESS_KEY:
                client_kwargs["aws_access_key_id"] = settings.STORAGE_ACCESS_KEY
            if settings.STORAGE_SECRET_KEY:
                client_kwargs["aws_secret_access_key"] = settings.STORAGE_SECRET_KEY
            
            self._client = boto3.client(**client_kwargs)
        
        return self._client
    
    def generate_key(
        self, 
        case_id: uuid.UUID, 
        media_type: str, 
        extension: str
    ) -> str:
        """
        Generate a unique storage key for a media file.
        Format: diagnosis/{case_id}/{media_type}/{timestamp}_{uuid}.{ext}
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_uuid = uuid.uuid4().hex[:8]
        return f"diagnosis/{case_id}/{media_type}/{timestamp}_{file_uuid}.{extension}"
    
    async def upload_file(
        self, 
        file_data: BinaryIO, 
        key: str, 
        content_type: str
    ) -> str:
        """
        Upload a file to object storage.
        Returns the storage path.
        """
        client = self._get_client()
        
        client.upload_fileobj(
            file_data,
            self.bucket,
            key,
            ExtraArgs={"ContentType": content_type}
        )
        
        return f"s3://{self.bucket}/{key}"
    
    async def delete_file(self, key: str) -> bool:
        """Delete a file from object storage."""
        try:
            client = self._get_client()
            client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False
    
    def get_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for file access."""
        client = self._get_client()
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in
        )


# Singleton instance
storage_client = StorageClient()
