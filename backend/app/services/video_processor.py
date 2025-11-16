"""
Video Processor Service
Handles video preprocessing: audio extraction, metadata, etc.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Optional

import ffmpeg

from app.core.config import settings

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Handles video preprocessing and metadata extraction"""

    def extract_audio(
        self,
        video_path: str,
        output_path: str,
    ) -> str:
        """
        Extract audio from video

        Args:
            video_path: Path to video file
            output_path: Output audio file path

        Returns:
            Path to extracted audio file
        """
        video_path = Path(video_path)
        output_path = Path(output_path)

        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Extracting audio from {video_path}")

        try:
            # Extract audio using FFmpeg
            stream = ffmpeg.input(str(video_path))
            stream = ffmpeg.output(
                stream,
                str(output_path),
                acodec=settings.ffmpeg.audio_codec,
                ar=settings.ffmpeg.audio_sample_rate,
                ac=1,  # Mono
            )

            ffmpeg.run(
                stream,
                overwrite_output=True,
                capture_stdout=True,
                capture_stderr=True,
                quiet=True,
            )

            logger.info(f"Audio extracted to {output_path}")

            return str(output_path)

        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error: {e.stderr.decode()}")
            raise RuntimeError(f"Audio extraction failed: {e.stderr.decode()}")

    def get_video_metadata(self, video_path: str) -> Dict:
        """
        Get video metadata using ffprobe

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video metadata
        """
        video_path = Path(video_path)

        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        try:
            probe = ffmpeg.probe(str(video_path))

            # Extract video stream info
            video_stream = next(
                (s for s in probe["streams"] if s["codec_type"] == "video"),
                None,
            )

            # Extract audio stream info
            audio_stream = next(
                (s for s in probe["streams"] if s["codec_type"] == "audio"),
                None,
            )

            # Get format info
            format_info = probe["format"]

            metadata = {
                "duration": float(format_info.get("duration", 0)),
                "size": int(format_info.get("size", 0)),
                "bit_rate": int(format_info.get("bit_rate", 0)),
                "format_name": format_info.get("format_name", "unknown"),
            }

            if video_stream:
                metadata.update(
                    {
                        "width": int(video_stream.get("width", 0)),
                        "height": int(video_stream.get("height", 0)),
                        "fps": self._parse_fps(video_stream.get("r_frame_rate", "0/1")),
                        "video_codec": video_stream.get("codec_name", "unknown"),
                    }
                )

            if audio_stream:
                metadata.update(
                    {
                        "audio_codec": audio_stream.get("codec_name", "unknown"),
                        "sample_rate": int(audio_stream.get("sample_rate", 0)),
                        "channels": int(audio_stream.get("channels", 0)),
                    }
                )

            logger.info(f"Video metadata: duration={metadata['duration']:.1f}s, "
                       f"{metadata.get('width')}x{metadata.get('height')}")

            return metadata

        except ffmpeg.Error as e:
            logger.error(f"FFprobe error: {str(e)}")
            raise RuntimeError(f"Failed to get video metadata: {str(e)}")

    def _parse_fps(self, fps_str: str) -> float:
        """Parse frame rate string (e.g., '30/1' -> 30.0)"""
        try:
            num, den = fps_str.split("/")
            return float(num) / float(den) if float(den) != 0 else 0.0
        except:
            return 0.0

    def validate_video(self, video_path: str) -> bool:
        """
        Validate video file can be processed

        Args:
            video_path: Path to video file

        Returns:
            True if valid, raises exception otherwise
        """
        try:
            metadata = self.get_video_metadata(video_path)

            # Check duration
            max_duration = settings.video.max_duration_hours * 3600
            if metadata["duration"] > max_duration:
                raise ValueError(
                    f"Video too long: {metadata['duration']:.1f}s "
                    f"(max: {max_duration}s)"
                )

            # Check has video stream
            if metadata.get("width", 0) == 0:
                raise ValueError("No video stream found")

            # Check has audio stream
            if metadata.get("sample_rate", 0) == 0:
                logger.warning("No audio stream found - transcription will be empty")

            return True

        except Exception as e:
            logger.error(f"Video validation failed: {str(e)}")
            raise

    def create_thumbnail(
        self,
        video_path: str,
        output_path: str,
        timestamp: float = 1.0,
        width: int = 320,
    ) -> str:
        """
        Create a thumbnail from video at given timestamp

        Args:
            video_path: Path to video file
            output_path: Output image path
            timestamp: Time in seconds to capture
            width: Thumbnail width

        Returns:
            Path to thumbnail file
        """
        video_path = Path(video_path)
        output_path = Path(output_path)

        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            stream = ffmpeg.input(str(video_path), ss=timestamp)
            stream = ffmpeg.filter(stream, "scale", width, -1)
            stream = ffmpeg.output(stream, str(output_path), vframes=1)

            ffmpeg.run(
                stream,
                overwrite_output=True,
                capture_stdout=True,
                capture_stderr=True,
                quiet=True,
            )

            logger.info(f"Thumbnail created: {output_path}")

            return str(output_path)

        except ffmpeg.Error as e:
            logger.error(f"Thumbnail creation failed: {e.stderr.decode()}")
            raise RuntimeError(f"Thumbnail creation failed: {e.stderr.decode()}")
