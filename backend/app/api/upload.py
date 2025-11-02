from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List
from app.core.security import get_current_user
from app.models.user import User
from app.services.s3_service import s3_service

router = APIRouter()


@router.post("/images")
async def upload_images(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload multiple product images to S3
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 images allowed per upload"
        )
    
    uploaded_urls = []
    
    for file in files:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename} is not an image"
            )
        
        # Read file content
        content = await file.read()
        
        # Upload to S3
        file_url = s3_service.upload_file(
            file_content=content,
            filename=file.filename,
            content_type=file.content_type
        )
        
        if not file_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload {file.filename}"
            )
        
        uploaded_urls.append(file_url)
    
    return {
        "uploaded_images": uploaded_urls,
        "count": len(uploaded_urls)
    }


@router.post("/presigned-url")
async def get_presigned_url(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a presigned URL for direct client-side upload
    """
    result = s3_service.generate_presigned_url(filename)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate presigned URL"
        )
    
    return result


@router.delete("/images")
async def delete_image(
    image_url: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete an image from S3
    """
    success = s3_service.delete_file(image_url)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete image"
        )
    
    return {"message": "Image deleted successfully"}

