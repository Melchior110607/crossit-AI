import boto3
from botocore.exceptions import ClientError
from typing import Optional
import uuid
from datetime import datetime
from app.core.config import settings


class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.AWS_S3_BUCKET

    def upload_file(
        self,
        file_content: bytes,
        filename: str,
        content_type: str = "image/jpeg"
    ) -> Optional[str]:
        """
        Upload a file to S3 and return the URL
        """
        try:
            # Generate unique filename
            file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
            unique_filename = f"products/{datetime.now().year}/{uuid.uuid4()}.{file_extension}"

            # Upload file
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=file_content,
                ContentType=content_type,
                ACL='public-read'  # Make file publicly accessible
            )

            # Generate URL
            file_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_filename}"
            return file_url

        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return None

    def delete_file(self, file_url: str) -> bool:
        """
        Delete a file from S3 given its URL
        """
        try:
            # Extract key from URL
            key = file_url.split(f"{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/")[-1]

            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True

        except ClientError as e:
            print(f"Error deleting file from S3: {e}")
            return False

    def generate_presigned_url(
        self,
        filename: str,
        expiration: int = 3600
    ) -> Optional[str]:
        """
        Generate a presigned URL for uploading files directly from client
        """
        try:
            file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
            unique_filename = f"products/{datetime.now().year}/{uuid.uuid4()}.{file_extension}"

            presigned_url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': unique_filename,
                    'ContentType': 'image/jpeg'
                },
                ExpiresIn=expiration
            )

            file_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_filename}"

            return {
                "upload_url": presigned_url,
                "file_url": file_url,
                "key": unique_filename
            }

        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None


s3_service = S3Service()

