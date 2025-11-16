"""
Scene Detection Service
Uses PySceneDetect to identify scene changes and shot boundaries
"""

import logging
from pathlib import Path
from typing import List

from scenedetect import detect, ContentDetector, AdaptiveDetector

from app.core.config import settings
from app.models.schemas import Scene

logger = logging.getLogger(__name__)


class SceneDetectionService:
    """Handles scene detection in videos"""

    def detect_scenes(self, video_path: str) -> List[Scene]:
        """
        Detect scenes in a video

        Args:
            video_path: Path to video file

        Returns:
            List of Scene objects with start/end times
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        logger.info(f"Detecting scenes in: {video_path}")

        # Choose detector based on config
        if settings.scene_detection.method == "content":
            detector = ContentDetector(
                threshold=settings.scene_detection.threshold,
                min_scene_len=settings.scene_detection.min_scene_len,
            )
        elif settings.scene_detection.method == "adaptive":
            detector = AdaptiveDetector(
                adaptive_threshold=settings.scene_detection.threshold,
                min_scene_len=settings.scene_detection.min_scene_len,
            )
        else:
            # Default to content
            detector = ContentDetector(
                threshold=settings.scene_detection.threshold,
                min_scene_len=settings.scene_detection.min_scene_len,
            )

        # Detect scenes
        scene_list = detect(str(video_path), detector)

        # Convert to our schema
        scenes = []
        for i, (start_time, end_time) in enumerate(scene_list):
            scene = Scene(
                start_time=start_time.get_seconds(),
                end_time=end_time.get_seconds(),
                duration=(end_time - start_time).get_seconds(),
                frame_count=end_time.get_frames() - start_time.get_frames(),
            )
            scenes.append(scene)

        logger.info(f"Detected {len(scenes)} scenes")

        return scenes

    def merge_short_scenes(
        self,
        scenes: List[Scene],
        min_duration: float = 3.0,
    ) -> List[Scene]:
        """
        Merge very short scenes to create more stable segments

        Args:
            scenes: List of scenes
            min_duration: Minimum scene duration in seconds

        Returns:
            List of merged scenes
        """
        if not scenes:
            return []

        merged = []
        current_scene = scenes[0]

        for next_scene in scenes[1:]:
            if current_scene.duration < min_duration:
                # Merge with next scene
                current_scene = Scene(
                    start_time=current_scene.start_time,
                    end_time=next_scene.end_time,
                    duration=next_scene.end_time - current_scene.start_time,
                    frame_count=current_scene.frame_count + next_scene.frame_count,
                )
            else:
                merged.append(current_scene)
                current_scene = next_scene

        # Add last scene
        merged.append(current_scene)

        logger.info(f"Merged {len(scenes)} scenes into {len(merged)} scenes")

        return merged
