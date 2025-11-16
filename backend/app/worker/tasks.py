"""
Celery Tasks
Main video processing pipeline
"""

import logging
from pathlib import Path

from celery import Task

from app.core.config import settings
from app.models.schemas import ProcessingStep
from app.services.clip_generator import ClipGenerator
from app.services.highlight_scorer import HighlightScorer
from app.services.job_manager import JobManager
from app.services.scene_detection import SceneDetectionService
from app.services.transcription import TranscriptionService
from app.services.video_processor import VideoProcessor
from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


class ProcessVideoTask(Task):
    """Base task with error handling"""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        job_id = args[0] if args else None

        if job_id:
            job_manager = JobManager()
            job_manager.update_job_status(
                job_id,
                "failed",
                error=str(exc),
            )

        logger.error(
            f"Task {task_id} failed for job {job_id}: {str(exc)}",
            exc_info=True,
        )


@celery_app.task(base=ProcessVideoTask, bind=True)
def process_video_task(self, job_id: str):
    """
    Main video processing pipeline

    Steps:
    1. Extract audio
    2. Transcribe with Whisper
    3. Detect scenes
    4. Score highlights
    5. Generate clips
    6. Generate captions

    Args:
        job_id: Job ID to process
    """
    logger.info(f"Starting processing for job {job_id}")

    job_manager = JobManager()

    # Initialize services
    video_processor = VideoProcessor()
    transcription_service = TranscriptionService()
    scene_detector = SceneDetectionService()
    highlight_scorer = HighlightScorer()
    clip_generator = ClipGenerator()

    try:
        # Get job
        job = job_manager.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Get video path
        upload_dir = Path(settings.storage.uploads_path) / job_id
        video_files = list(upload_dir.glob("original.*"))

        if not video_files:
            raise FileNotFoundError(f"Video file not found for job {job_id}")

        video_path = str(video_files[0])

        # Step 1: Validate and get video metadata
        logger.info(f"[{job_id}] Step 1: Validating video")
        job_manager.update_job_progress(
            job_id,
            ProcessingStep.EXTRACTING_AUDIO,
            10,
            "Validating video...",
        )

        video_processor.validate_video(video_path)
        metadata = video_processor.get_video_metadata(video_path)
        job_manager.update_job_duration(job_id, metadata["duration"])

        # Step 2: Extract audio
        logger.info(f"[{job_id}] Step 2: Extracting audio")
        job_manager.update_job_progress(
            job_id,
            ProcessingStep.EXTRACTING_AUDIO,
            20,
            "Extracting audio...",
        )

        temp_dir = Path(settings.storage.temp_path) / job_id
        temp_dir.mkdir(parents=True, exist_ok=True)

        audio_path = str(temp_dir / "audio.wav")
        video_processor.extract_audio(video_path, audio_path)

        # Step 3: Transcribe
        logger.info(f"[{job_id}] Step 3: Transcribing audio")
        job_manager.update_job_progress(
            job_id,
            ProcessingStep.TRANSCRIBING,
            30,
            "Transcribing audio with Whisper...",
        )

        transcript = transcription_service.transcribe(audio_path)

        # Generate full SRT for reference
        captions_dir = Path(settings.storage.captions_path) / job_id
        captions_dir.mkdir(parents=True, exist_ok=True)
        full_srt_path = str(captions_dir / "full_transcript.srt")
        transcription_service.generate_srt(transcript, full_srt_path)

        logger.info(
            f"[{job_id}] Transcription complete: {len(transcript.segments)} segments"
        )

        # Step 4: Detect scenes
        logger.info(f"[{job_id}] Step 4: Detecting scenes")
        job_manager.update_job_progress(
            job_id,
            ProcessingStep.DETECTING_SCENES,
            50,
            "Detecting scenes...",
        )

        scenes = scene_detector.detect_scenes(video_path)

        # Merge very short scenes
        scenes = scene_detector.merge_short_scenes(scenes, min_duration=2.0)

        logger.info(f"[{job_id}] Detected {len(scenes)} scenes")

        # Step 5: Score highlights
        logger.info(f"[{job_id}] Step 5: Scoring highlights")
        job_manager.update_job_progress(
            job_id,
            ProcessingStep.SCORING_HIGHLIGHTS,
            60,
            "Identifying highlights...",
        )

        highlights = highlight_scorer.score_highlights(
            video_path=video_path,
            audio_path=audio_path,
            transcript=transcript,
            scenes=scenes,
        )

        logger.info(f"[{job_id}] Identified {len(highlights)} highlights")

        if not highlights:
            raise ValueError("No highlights found - video may be too short or quiet")

        # Step 6: Generate clips
        logger.info(f"[{job_id}] Step 6: Generating clips")
        job_manager.update_job_progress(
            job_id,
            ProcessingStep.GENERATING_CLIPS,
            70,
            "Generating video clips...",
        )

        clips = clip_generator.generate_clips(
            job_id=job_id,
            video_path=video_path,
            highlights=highlights,
            transcript=transcript,
        )

        logger.info(f"[{job_id}] Generated {len(clips)} clips")

        # Save clips to job
        job_manager.save_clips(job_id, clips)

        # Step 7: Complete
        logger.info(f"[{job_id}] Step 7: Complete")
        job_manager.update_job_progress(
            job_id,
            ProcessingStep.COMPLETED,
            100,
            f"Processing complete! Generated {len(clips)} clips",
        )

        job_manager.update_job_status(job_id, "completed")

        logger.info(f"Processing complete for job {job_id}")

        return {
            "job_id": job_id,
            "clips_count": len(clips),
            "duration": metadata["duration"],
        }

    except Exception as e:
        logger.error(f"Processing failed for job {job_id}: {str(e)}", exc_info=True)
        job_manager.update_job_status(job_id, "failed", error=str(e))
        raise
