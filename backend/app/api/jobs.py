"""
Jobs API endpoints
Handles job management, clip generation, and clip operations
"""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.models.schemas import (
    Job,
    JobResponse,
    ClipResponse,
    Clip,
    TrimRequest,
)
from app.services.job_manager import JobManager
from app.worker.tasks import process_video_task

logger = logging.getLogger(__name__)
router = APIRouter()
job_manager = JobManager()


@router.get("/jobs", response_model=List[Job])
async def list_jobs() -> List[Job]:
    """
    List all jobs

    Returns list of all jobs with their current status
    """
    return job_manager.list_jobs()


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str) -> JobResponse:
    """
    Get job details

    - **job_id**: Job ID

    Returns detailed job information including progress
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    return JobResponse(job=job)


@router.post("/jobs/{job_id}/generate")
async def generate_clips(job_id: str) -> JSONResponse:
    """
    Start clip generation for a job

    - **job_id**: Job ID

    Enqueues the video processing task
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    if job.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job already {job.status}",
        )

    try:
        # Enqueue processing task
        task = process_video_task.delay(job_id)
        logger.info(f"Enqueued processing task for job {job_id}: {task.id}")

        # Update job status
        job_manager.update_job_status(job_id, "processing")

        return JSONResponse(
            content={
                "message": "Clip generation started",
                "job_id": job_id,
                "task_id": task.id,
            }
        )

    except Exception as e:
        logger.error(f"Failed to start processing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start processing: {str(e)}",
        )


@router.get("/jobs/{job_id}/clips", response_model=ClipResponse)
async def get_clips(job_id: str) -> ClipResponse:
    """
    Get all clips for a job

    - **job_id**: Job ID

    Returns list of generated clips with download URLs
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    clips = job_manager.get_clips(job_id)

    return ClipResponse(clips=clips, total=len(clips))


@router.get("/jobs/{job_id}/clips/{clip_id}", response_model=Clip)
async def get_clip(job_id: str, clip_id: str) -> Clip:
    """
    Get a specific clip

    - **job_id**: Job ID
    - **clip_id**: Clip ID

    Returns clip details
    """
    clip = job_manager.get_clip(job_id, clip_id)
    if not clip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clip {clip_id} not found",
        )

    return clip


@router.post("/jobs/{job_id}/clips/{clip_id}/trim", response_model=Clip)
async def trim_clip(job_id: str, clip_id: str, request: TrimRequest) -> Clip:
    """
    Trim/re-export a clip with new start/end times

    - **job_id**: Job ID
    - **clip_id**: Clip ID
    - **request**: Trim request with new start/end times

    Returns updated clip information
    """
    # Validate times
    if request.end_time <= request.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be greater than start time",
        )

    duration = request.end_time - request.start_time
    if duration < 1 or duration > 300:  # 5 minutes max
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Clip duration must be between 1 and 300 seconds",
        )

    try:
        # Get original clip
        original_clip = job_manager.get_clip(job_id, clip_id)
        if not original_clip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Clip {clip_id} not found",
            )

        # Re-export clip with new times
        from app.services.clip_generator import ClipGenerator

        clip_generator = ClipGenerator()
        new_clip = await clip_generator.trim_clip(
            job_id=job_id,
            clip_id=clip_id,
            start_time=request.start_time,
            end_time=request.end_time,
            aspect_ratio=request.aspect_ratio or original_clip.aspect_ratio,
        )

        # Update clip in job manager
        job_manager.update_clip(job_id, clip_id, new_clip)

        return new_clip

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trim clip: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trim clip: {str(e)}",
        )


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str) -> JSONResponse:
    """
    Delete a job and all its associated files

    - **job_id**: Job ID

    Permanently deletes the job and all generated clips
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    try:
        job_manager.delete_job(job_id)
        return JSONResponse(content={"message": f"Job {job_id} deleted"})
    except Exception as e:
        logger.error(f"Failed to delete job: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete job: {str(e)}",
        )
