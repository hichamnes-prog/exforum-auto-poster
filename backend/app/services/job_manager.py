"""
Job Manager Service
Manages job state and metadata using JSON files
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.core.config import settings
from app.models.schemas import (
    Job,
    JobStatus,
    Clip,
    ProcessingProgress,
    ProcessingStep,
)

logger = logging.getLogger(__name__)


class JobManager:
    """Manages jobs and their metadata"""

    def __init__(self):
        self.jobs_dir = Path(settings.storage.base_path) / "jobs"
        self.jobs_dir.mkdir(parents=True, exist_ok=True)

    def _get_job_file(self, job_id: str) -> Path:
        """Get path to job metadata file"""
        return self.jobs_dir / f"{job_id}.json"

    def _get_clips_file(self, job_id: str) -> Path:
        """Get path to clips metadata file"""
        return self.jobs_dir / f"{job_id}_clips.json"

    def create_job(
        self,
        job_id: str,
        filename: str,
        file_size: int,
        video_path: str,
        duration: Optional[float] = None,
    ) -> Job:
        """Create a new job"""
        now = datetime.utcnow()

        job = Job(
            id=job_id,
            status=JobStatus.PENDING,
            filename=filename,
            file_size=file_size,
            duration=duration,
            created_at=now,
            updated_at=now,
            video_url=f"/storage/uploads/{job_id}/original{Path(filename).suffix}",
            clips_count=0,
        )

        # Save job metadata
        self._save_job(job)

        logger.info(f"Created job {job_id}: {filename}")
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        job_file = self._get_job_file(job_id)

        if not job_file.exists():
            return None

        try:
            with open(job_file, "r") as f:
                data = json.load(f)
                return Job(**data)
        except Exception as e:
            logger.error(f"Failed to load job {job_id}: {str(e)}")
            return None

    def list_jobs(self) -> List[Job]:
        """List all jobs"""
        jobs = []

        for job_file in self.jobs_dir.glob("*.json"):
            if not job_file.name.endswith("_clips.json"):
                try:
                    with open(job_file, "r") as f:
                        data = json.load(f)
                        jobs.append(Job(**data))
                except Exception as e:
                    logger.error(f"Failed to load job from {job_file}: {str(e)}")

        # Sort by created_at descending
        jobs.sort(key=lambda j: j.created_at, reverse=True)
        return jobs

    def update_job_status(
        self,
        job_id: str,
        status: str,
        error: Optional[str] = None,
        progress: Optional[ProcessingProgress] = None,
    ) -> Optional[Job]:
        """Update job status"""
        job = self.get_job(job_id)
        if not job:
            return None

        job.status = JobStatus(status)
        job.updated_at = datetime.utcnow()

        if error:
            job.error = error

        if progress:
            job.progress = progress

        self._save_job(job)
        return job

    def update_job_progress(
        self,
        job_id: str,
        step: ProcessingStep,
        progress: float,
        message: str,
        current_clip: Optional[int] = None,
        total_clips: Optional[int] = None,
    ) -> Optional[Job]:
        """Update job processing progress"""
        progress_obj = ProcessingProgress(
            step=step,
            progress=progress,
            message=message,
            current_clip=current_clip,
            total_clips=total_clips,
        )

        return self.update_job_status(job_id, "processing", progress=progress_obj)

    def update_job_duration(self, job_id: str, duration: float) -> Optional[Job]:
        """Update job video duration"""
        job = self.get_job(job_id)
        if not job:
            return None

        job.duration = duration
        job.updated_at = datetime.utcnow()
        self._save_job(job)
        return job

    def _save_job(self, job: Job) -> None:
        """Save job to file"""
        job_file = self._get_job_file(job.id)

        with open(job_file, "w") as f:
            json.dump(job.model_dump(mode="json"), f, indent=2, default=str)

    def get_clips(self, job_id: str) -> List[Clip]:
        """Get all clips for a job"""
        clips_file = self._get_clips_file(job_id)

        if not clips_file.exists():
            return []

        try:
            with open(clips_file, "r") as f:
                data = json.load(f)
                return [Clip(**clip) for clip in data]
        except Exception as e:
            logger.error(f"Failed to load clips for job {job_id}: {str(e)}")
            return []

    def get_clip(self, job_id: str, clip_id: str) -> Optional[Clip]:
        """Get a specific clip"""
        clips = self.get_clips(job_id)

        for clip in clips:
            if clip.id == clip_id:
                return clip

        return None

    def save_clips(self, job_id: str, clips: List[Clip]) -> None:
        """Save clips for a job"""
        clips_file = self._get_clips_file(job_id)

        with open(clips_file, "w") as f:
            json.dump(
                [clip.model_dump(mode="json") for clip in clips],
                f,
                indent=2,
                default=str,
            )

        # Update job clips count
        job = self.get_job(job_id)
        if job:
            job.clips_count = len(clips)
            job.updated_at = datetime.utcnow()
            self._save_job(job)

        logger.info(f"Saved {len(clips)} clips for job {job_id}")

    def update_clip(self, job_id: str, clip_id: str, updated_clip: Clip) -> None:
        """Update a specific clip"""
        clips = self.get_clips(job_id)

        for i, clip in enumerate(clips):
            if clip.id == clip_id:
                clips[i] = updated_clip
                break

        self.save_clips(job_id, clips)

    def delete_job(self, job_id: str) -> None:
        """Delete a job and all associated files"""
        # Delete job metadata files
        job_file = self._get_job_file(job_id)
        if job_file.exists():
            job_file.unlink()

        clips_file = self._get_clips_file(job_id)
        if clips_file.exists():
            clips_file.unlink()

        # Delete storage directories
        upload_dir = Path(settings.storage.uploads_path) / job_id
        if upload_dir.exists():
            shutil.rmtree(upload_dir)

        clips_dir = Path(settings.storage.clips_path) / job_id
        if clips_dir.exists():
            shutil.rmtree(clips_dir)

        captions_dir = Path(settings.storage.captions_path) / job_id
        if captions_dir.exists():
            shutil.rmtree(captions_dir)

        logger.info(f"Deleted job {job_id}")
