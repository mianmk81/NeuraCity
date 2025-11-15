"""Image handling service for file uploads."""
import os
import uuid
from fastapi import UploadFile, HTTPException
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


async def validate_image(file: UploadFile) -> bool:
    """Validate image file type and size."""
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
        )
    
    content = await file.read()
    await file.seek(0)
    
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB"
        )
    
    return True


async def save_image(file: UploadFile) -> str:
    """Save uploaded image and return filename."""
    try:
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        filename = f"issue_{uuid.uuid4().hex[:12]}.{ext}"
        filepath = os.path.join(settings.UPLOAD_DIR, filename)
        
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        content = await file.read()
        with open(filepath, 'wb') as f:
            f.write(content)
        
        logger.info(f"Saved image: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error saving image: {e}")
        raise HTTPException(status_code=500, detail="Failed to save image")


def delete_image(filename: str) -> bool:
    """Delete image file."""
    try:
        filepath = os.path.join(settings.UPLOAD_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Deleted image: {filename}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting image: {e}")
        return False


def get_image_url(filename: str) -> str:
    """Generate image URL."""
    return f"/{settings.UPLOAD_DIR}/{filename}"
