"""
Upload API endpoints
Handles video file uploads
"""

import logging
import uuid
from pathlib import Path
from typing import Optional

import aiofiles
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.models.schemas import UploadResponse, JobCreate
from app.services.job_manager import JobManager

logger = logging.getLogger(__name__)
router = APIRouter()
job_manager = JobManager()

# Allowed video file extensions
ALLOWED_EXTENSIONS = {
    ".mp4", ".mov", ".avi", ".mkv", ".webm",
    ".flv", ".wmv", ".m4v", ".mpg", ".mpeg"
}


def validate_video_file(filename: str, file_size: int) -> None:
    """Validate uploaded video file"""
    # Check file extension
    file_ext = Path(filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Check file size
    max_size_bytes = settings.video.max_upload_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.video.max_upload_size_mb}MB",
        )


@router.post("/upload", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(..., description="Video file to upload"),
) -> UploadResponse:
    """
    Upload a video file for processing

    - **file**: Video file (MP4, MOV, AVI, etc.)

    Returns job ID and upload confirmation
    """
    try:
        # Get file info
        filename = file.filename or "video.mp4"
        file_size = 0

        # Read file in chunks to get size
        chunk_size = 1024 * 1024  # 1MB chunks
        chunks = []

        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            chunks.append(chunk)
            file_size += len(chunk)

        # Validate file
        validate_video_file(filename, file_size)

        # Generate job ID
        job_id = str(uuid.uuid4())

        # Create upload directory
        upload_dir = Path(settings.storage.uploads_path) / job_id
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_ext = Path(filename).suffix
        video_path = upload_dir / f"original{file_ext}"

        async with aiofiles.open(video_path, "wb") as f:
            for chunk in chunks:
                await f.write(chunk)

        logger.info(f"Uploaded video: {filename} ({file_size} bytes) -> {video_path}")

        # Create job
        job = job_manager.create_job(
            job_id=job_id,
            filename=filename,
            file_size=file_size,
            video_path=str(video_path),
        )

        return UploadResponse(
            job_id=job_id,
            filename=filename,
            file_size=file_size,
            message="Video uploaded successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}",
        )
