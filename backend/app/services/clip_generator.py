"""
Clip Generator Service
Generates video clips using FFmpeg with various aspect ratios and captions
"""

import logging
import subprocess
import uuid
from pathlib import Path
from typing import Optional, Tuple

import ffmpeg

from app.core.config import settings
from app.models.schemas import Clip, HighlightCandidate, Transcript

logger = logging.getLogger(__name__)


class ClipGenerator:
    """Generates video clips from highlights"""

    def __init__(self):
        self.clips_config = settings.clips
        self.captions_config = settings.captions
        self.ffmpeg_config = settings.ffmpeg

    def generate_clips(
        self,
        job_id: str,
        video_path: str,
        highlights: list[HighlightCandidate],
        transcript: Transcript,
    ) -> list[Clip]:
        """
        Generate clips from highlights

        Args:
            job_id: Job ID
            video_path: Path to source video
            highlights: List of highlight candidates
            transcript: Full transcript

        Returns:
            List of generated clips
        """
        clips = []

        # Create output directories
        clips_dir = Path(settings.storage.clips_path) / job_id
        clips_dir.mkdir(parents=True, exist_ok=True)

        captions_dir = Path(settings.storage.captions_path) / job_id
        captions_dir.mkdir(parents=True, exist_ok=True)

        # Get enabled aspect ratios
        aspect_ratios = [
            ar for ar in self.clips_config.aspect_ratios if ar.enabled
        ]

        if not aspect_ratios:
            logger.warning("No aspect ratios enabled, using default 16:9")
            from app.core.config import AspectRatio
            aspect_ratios = [
                AspectRatio(name="landscape", ratio="16:9", width=1920, height=1080)
            ]

        # Generate clips for each highlight and aspect ratio
        for i, highlight in enumerate(highlights):
            for aspect_ratio in aspect_ratios:
                try:
                    clip = self._generate_clip(
                        job_id=job_id,
                        video_path=video_path,
                        highlight=highlight,
                        aspect_ratio=aspect_ratio,
                        transcript=transcript,
                        index=i,
                    )

                    if clip:
                        clips.append(clip)

                except Exception as e:
                    logger.error(
                        f"Failed to generate clip {i} ({aspect_ratio.name}): {str(e)}"
                    )

        logger.info(f"Generated {len(clips)} clips for job {job_id}")

        return clips

    def _generate_clip(
        self,
        job_id: str,
        video_path: str,
        highlight: HighlightCandidate,
        aspect_ratio,
        transcript: Transcript,
        index: int,
    ) -> Optional[Clip]:
        """Generate a single clip"""
        clip_id = str(uuid.uuid4())

        # Output paths
        clips_dir = Path(settings.storage.clips_path) / job_id
        captions_dir = Path(settings.storage.captions_path) / job_id

        clip_filename = f"clip_{index:03d}_{aspect_ratio.name}.mp4"
        clip_path = clips_dir / clip_filename

        srt_filename = f"clip_{index:03d}_{aspect_ratio.name}.srt"
        srt_path = captions_dir / srt_filename

        # Generate SRT caption file for this clip
        self._generate_clip_srt(
            transcript=transcript,
            start_time=highlight.start_time,
            end_time=highlight.end_time,
            output_path=str(srt_path),
        )

        # Generate video clip
        self._create_video_clip(
            input_path=video_path,
            output_path=str(clip_path),
            start_time=highlight.start_time,
            end_time=highlight.end_time,
            width=aspect_ratio.width,
            height=aspect_ratio.height,
            srt_path=str(srt_path),
        )

        # Create clip object
        clip = Clip(
            id=clip_id,
            job_id=job_id,
            start_time=highlight.start_time,
            end_time=highlight.end_time,
            duration=highlight.duration,
            aspect_ratio=aspect_ratio.ratio,
            score=highlight.score,
            video_url=f"/storage/clips/{job_id}/{clip_filename}",
            caption_url=f"/storage/captions/{job_id}/{srt_filename}",
            transcript=highlight.transcript,
        )

        logger.info(f"Generated clip: {clip_filename}")

        return clip

    def _create_video_clip(
        self,
        input_path: str,
        output_path: str,
        start_time: float,
        end_time: float,
        width: int,
        height: int,
        srt_path: Optional[str] = None,
    ) -> None:
        """
        Create a video clip using FFmpeg

        Args:
            input_path: Source video path
            output_path: Output clip path
            start_time: Start time in seconds
            end_time: End time in seconds
            width: Output width
            height: Output height
            srt_path: Optional SRT file for burned-in captions
        """
        duration = end_time - start_time

        # Build FFmpeg command
        input_stream = ffmpeg.input(input_path, ss=start_time, t=duration)

        # Scale and crop to target aspect ratio
        # Use smart scaling: scale to fit, then center crop
        video = input_stream.video

        # Scale to cover the target dimensions (one dimension will exceed)
        video = video.filter("scale", width, height, force_original_aspect_ratio="increase")

        # Center crop to exact dimensions
        video = video.filter("crop", width, height)

        # Burn in captions if provided
        if srt_path and Path(srt_path).exists():
            # Build subtitle filter
            subtitle_style = self._build_subtitle_style()
            video = video.filter("subtitles", srt_path, **subtitle_style)

        # Audio
        audio = input_stream.audio

        # Output with encoding settings
        output = ffmpeg.output(
            video,
            audio,
            output_path,
            vcodec=self.ffmpeg_config.video_codec,
            preset=self.ffmpeg_config.video_preset,
            crf=self.ffmpeg_config.video_crf,
            acodec="aac",
            audio_bitrate=self.ffmpeg_config.audio_bitrate,
            **{"movflags": "+faststart"},  # Enable progressive streaming
        )

        # Run FFmpeg
        try:
            ffmpeg.run(
                output,
                overwrite_output=True,
                capture_stdout=True,
                capture_stderr=True,
                quiet=True,
            )
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error: {e.stderr.decode()}")
            raise

    def _build_subtitle_style(self) -> dict:
        """Build subtitle filter style parameters"""
        # Note: FFmpeg subtitles filter uses ASS/SSA format
        # We'll use force_style to customize appearance
        style = {
            "force_style": (
                f"FontName={self.captions_config.font_name},"
                f"FontSize={self.captions_config.font_size},"
                f"PrimaryColour=&H{self._color_to_ass(self.captions_config.font_color)},"
                f"OutlineColour=&H{self._color_to_ass(self.captions_config.font_outline_color)},"
                f"Outline={self.captions_config.font_outline_width},"
                f"Alignment={self._position_to_alignment(self.captions_config.position)},"
                f"MarginV={self.captions_config.margin}"
            )
        }

        return style

    def _color_to_ass(self, color: str) -> str:
        """Convert color name to ASS format (&HAABBGGRR)"""
        color_map = {
            "white": "FFFFFF",
            "black": "000000",
            "yellow": "00FFFF",
            "red": "0000FF",
            "green": "00FF00",
            "blue": "FF0000",
        }

        return color_map.get(color.lower(), "FFFFFF")

    def _position_to_alignment(self, position: str) -> int:
        """Convert position to ASS alignment code"""
        # ASS alignment: 1=left-bottom, 2=center-bottom, 3=right-bottom
        #               4=left-middle, 5=center-middle, 6=right-middle
        #               7=left-top, 8=center-top, 9=right-top
        position_map = {
            "bottom": 2,
            "center": 5,
            "top": 8,
        }

        return position_map.get(position.lower(), 2)

    def _generate_clip_srt(
        self,
        transcript: Transcript,
        start_time: float,
        end_time: float,
        output_path: str,
    ) -> None:
        """Generate SRT file for a specific clip time range"""

        def format_timestamp(seconds: float) -> str:
            """Format seconds to SRT timestamp"""
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

        # Extract segments that overlap with clip
        clip_segments = []

        for seg in transcript.segments:
            # Check if segment overlaps with clip time range
            if seg.start < end_time and seg.end > start_time:
                # Adjust segment times to be relative to clip start
                adjusted_seg = {
                    "text": seg.text,
                    "start": max(0, seg.start - start_time),
                    "end": min(end_time - start_time, seg.end - start_time),
                }
                clip_segments.append(adjusted_seg)

        # Write SRT file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            for i, seg in enumerate(clip_segments, 1):
                f.write(f"{i}\n")
                f.write(
                    f"{format_timestamp(seg['start'])} --> "
                    f"{format_timestamp(seg['end'])}\n"
                )
                f.write(f"{seg['text']}\n\n")

    async def trim_clip(
        self,
        job_id: str,
        clip_id: str,
        start_time: float,
        end_time: float,
        aspect_ratio: str,
    ) -> Clip:
        """
        Re-export a clip with adjusted start/end times

        Args:
            job_id: Job ID
            clip_id: Clip ID
            start_time: New start time
            end_time: New end time
            aspect_ratio: Aspect ratio (e.g., "16:9")

        Returns:
            Updated clip object
        """
        # Get original video path
        upload_dir = Path(settings.storage.uploads_path) / job_id
        video_files = list(upload_dir.glob("original.*"))

        if not video_files:
            raise FileNotFoundError(f"Original video not found for job {job_id}")

        video_path = str(video_files[0])

        # Find aspect ratio config
        ar_config = None
        for ar in self.clips_config.aspect_ratios:
            if ar.ratio == aspect_ratio:
                ar_config = ar
                break

        if not ar_config:
            raise ValueError(f"Invalid aspect ratio: {aspect_ratio}")

        # Load transcript (needed for captions)
        # For now, generate empty SRT - in production, load from job state
        from app.services.job_manager import JobManager

        job_manager = JobManager()
        clips = job_manager.get_clips(job_id)

        # Find original clip to get transcript
        original_clip = None
        for clip in clips:
            if clip.id == clip_id:
                original_clip = clip
                break

        # Create new clip with updated times
        clips_dir = Path(settings.storage.clips_path) / job_id
        captions_dir = Path(settings.storage.captions_path) / job_id

        new_clip_filename = f"clip_{clip_id}_trimmed.mp4"
        new_clip_path = clips_dir / new_clip_filename

        # Generate video (without captions for simplicity in trim)
        self._create_video_clip(
            input_path=video_path,
            output_path=str(new_clip_path),
            start_time=start_time,
            end_time=end_time,
            width=ar_config.width,
            height=ar_config.height,
        )

        # Create updated clip object
        new_clip = Clip(
            id=clip_id,
            job_id=job_id,
            start_time=start_time,
            end_time=end_time,
            duration=end_time - start_time,
            aspect_ratio=aspect_ratio,
            score=original_clip.score if original_clip else 0.0,
            video_url=f"/storage/clips/{job_id}/{new_clip_filename}",
            caption_url=original_clip.caption_url if original_clip else None,
            transcript=original_clip.transcript if original_clip else "",
        )

        logger.info(f"Trimmed clip {clip_id}: {start_time:.1f}s - {end_time:.1f}s")

        return new_clip
