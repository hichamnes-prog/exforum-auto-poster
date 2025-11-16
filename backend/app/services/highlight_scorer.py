"""
Highlight Scorer Service
Scores video segments to identify the best clips based on multiple factors:
- Speech density
- Audio energy
- Scene changes
- Duration preferences
"""

import logging
from pathlib import Path
from typing import List, Tuple

import librosa
import numpy as np

from app.core.config import settings
from app.models.schemas import (
    Transcript,
    Scene,
    HighlightCandidate,
    TranscriptSegment,
)

logger = logging.getLogger(__name__)


class HighlightScorer:
    """Scores video segments to identify highlights"""

    def __init__(self):
        self.config = settings.highlight_scoring
        self.clips_config = settings.clips

    def score_highlights(
        self,
        video_path: str,
        audio_path: str,
        transcript: Transcript,
        scenes: List[Scene],
    ) -> List[HighlightCandidate]:
        """
        Score potential highlight segments

        Args:
            video_path: Path to video file
            audio_path: Path to audio file
            transcript: Transcript with segments
            scenes: List of detected scenes

        Returns:
            List of scored highlight candidates, sorted by score
        """
        logger.info("Scoring highlights...")

        # Load audio for energy analysis
        audio_energy = self._load_audio_energy(audio_path)

        # Generate candidate windows
        candidates = self._generate_candidates(transcript, scenes)

        # Score each candidate
        scored_candidates = []
        for candidate in candidates:
            score = self._score_candidate(
                candidate,
                transcript,
                scenes,
                audio_energy,
            )

            if score >= self.config.min_score:
                candidate.score = score
                scored_candidates.append(candidate)

        # Sort by score descending
        scored_candidates.sort(key=lambda c: c.score, reverse=True)

        # Take top N clips
        top_candidates = scored_candidates[: self.clips_config.max_clips]

        logger.info(
            f"Scored {len(candidates)} candidates, "
            f"kept {len(top_candidates)} with score >= {self.config.min_score}"
        )

        return top_candidates

    def _generate_candidates(
        self,
        transcript: Transcript,
        scenes: List[Scene],
    ) -> List[HighlightCandidate]:
        """Generate candidate clip windows"""
        candidates = []

        min_dur = self.clips_config.min_duration
        max_dur = self.clips_config.max_duration
        target_dur = self.clips_config.target_duration

        # Strategy 1: Scene-based candidates
        # Create clips aligned with scene boundaries
        for scene in scenes:
            if min_dur <= scene.duration <= max_dur:
                candidate = self._create_candidate(
                    scene.start_time,
                    scene.end_time,
                    transcript,
                )
                if candidate:
                    candidates.append(candidate)

        # Strategy 2: Fixed-duration sliding windows
        # Slide windows across the video to catch highlights not aligned with scenes
        step = target_dur / 2  # 50% overlap

        for duration in [target_dur, min_dur + 5, max_dur - 5]:
            time = 0
            while time + duration <= transcript.duration:
                candidate = self._create_candidate(
                    time,
                    time + duration,
                    transcript,
                )
                if candidate:
                    candidates.append(candidate)
                time += step

        # Remove duplicates (similar start times)
        candidates = self._deduplicate_candidates(candidates)

        logger.info(f"Generated {len(candidates)} candidate clips")

        return candidates

    def _create_candidate(
        self,
        start_time: float,
        end_time: float,
        transcript: Transcript,
    ) -> HighlightCandidate:
        """Create a highlight candidate from time range"""
        # Get transcript text for this time range
        transcript_text = self._get_transcript_text(
            transcript,
            start_time,
            end_time,
        )

        # Calculate speech density (words per second)
        word_count = len(transcript_text.split())
        duration = end_time - start_time
        speech_density = word_count / duration if duration > 0 else 0

        # Only create candidate if it has some speech
        if speech_density < 0.5:  # At least 0.5 words per second
            return None

        return HighlightCandidate(
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            score=0.0,  # Will be calculated later
            speech_density=speech_density,
            audio_energy=0.0,  # Will be calculated later
            scene_changes=0,  # Will be calculated later
            transcript=transcript_text,
        )

    def _score_candidate(
        self,
        candidate: HighlightCandidate,
        transcript: Transcript,
        scenes: List[Scene],
        audio_energy: np.ndarray,
    ) -> float:
        """Score a single candidate based on multiple factors"""
        # 1. Speech density score (normalized 0-1)
        speech_score = min(
            candidate.speech_density / (self.config.min_speech_density * 2),
            1.0,
        )

        # 2. Audio energy score
        energy_score = self._calculate_audio_energy_score(
            candidate,
            audio_energy,
        )
        candidate.audio_energy = energy_score

        # 3. Scene change score (visual interest)
        scene_change_score = self._calculate_scene_change_score(
            candidate,
            scenes,
        )

        # 4. Sustained speech score (continuous talking)
        sustained_score = self._calculate_sustained_speech_score(
            candidate,
            transcript,
        )

        # 5. Duration penalty (prefer target duration)
        duration_score = self._calculate_duration_score(candidate)

        # Weighted combination
        total_score = (
            self.config.speech_density_weight * speech_score
            + self.config.audio_energy_weight * energy_score
            + self.config.scene_change_weight * scene_change_score
            + self.config.sustained_speech_weight * sustained_score
            + self.config.duration_penalty_weight * duration_score
        )

        return total_score

    def _load_audio_energy(self, audio_path: str) -> np.ndarray:
        """Load audio and calculate energy envelope"""
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=16000)

            # Calculate RMS energy
            hop_length = 512
            rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]

            # Smooth energy
            rms = librosa.util.normalize(rms)

            logger.info(f"Loaded audio energy: {len(rms)} frames")

            return rms

        except Exception as e:
            logger.error(f"Failed to load audio energy: {str(e)}")
            return np.array([0.5])  # Return neutral energy

    def _calculate_audio_energy_score(
        self,
        candidate: HighlightCandidate,
        audio_energy: np.ndarray,
    ) -> float:
        """Calculate normalized audio energy for time range"""
        if len(audio_energy) == 0:
            return 0.5

        # Convert time to audio frame indices
        hop_length = 512
        sr = 16000
        frame_rate = sr / hop_length

        start_frame = int(candidate.start_time * frame_rate)
        end_frame = int(candidate.end_time * frame_rate)

        # Extract energy for this segment
        segment_energy = audio_energy[start_frame:end_frame]

        if len(segment_energy) == 0:
            return 0.5

        # Use mean energy, normalized 0-1
        mean_energy = np.mean(segment_energy)
        return float(mean_energy)

    def _calculate_scene_change_score(
        self,
        candidate: HighlightCandidate,
        scenes: List[Scene],
    ) -> float:
        """Calculate scene change score (more changes = more visual interest)"""
        # Count scene boundaries within this clip
        scene_changes = 0

        for scene in scenes:
            # Check if scene boundary is within candidate
            if candidate.start_time < scene.start_time < candidate.end_time:
                scene_changes += 1

        candidate.scene_changes = scene_changes

        # Normalize: 2-3 scene changes is ideal for a short clip
        if scene_changes == 0:
            return 0.3  # Static = less interesting
        elif scene_changes <= 3:
            return 1.0  # Ideal
        else:
            return 0.7  # Too many = chaotic

    def _calculate_sustained_speech_score(
        self,
        candidate: HighlightCandidate,
        transcript: Transcript,
    ) -> float:
        """Calculate how sustained/continuous the speech is"""
        # Get segments that overlap with candidate
        overlapping_segments = []

        for seg in transcript.segments:
            if self._segments_overlap(
                seg.start,
                seg.end,
                candidate.start_time,
                candidate.end_time,
            ):
                overlapping_segments.append(seg)

        if not overlapping_segments:
            return 0.0

        # Calculate speech coverage (% of time with speech)
        speech_time = sum(
            min(seg.end, candidate.end_time) - max(seg.start, candidate.start_time)
            for seg in overlapping_segments
        )

        coverage = speech_time / candidate.duration
        return min(coverage, 1.0)

    def _calculate_duration_score(self, candidate: HighlightCandidate) -> float:
        """Penalize clips that are too far from target duration"""
        target = self.clips_config.target_duration
        diff = abs(candidate.duration - target)

        # Gaussian-like penalty
        score = np.exp(-(diff ** 2) / (2 * (target / 2) ** 2))
        return float(score)

    def _get_transcript_text(
        self,
        transcript: Transcript,
        start_time: float,
        end_time: float,
    ) -> str:
        """Extract transcript text for a time range"""
        texts = []

        for seg in transcript.segments:
            if self._segments_overlap(seg.start, seg.end, start_time, end_time):
                texts.append(seg.text)

        return " ".join(texts)

    def _segments_overlap(
        self,
        start1: float,
        end1: float,
        start2: float,
        end2: float,
    ) -> bool:
        """Check if two time segments overlap"""
        return start1 < end2 and start2 < end1

    def _deduplicate_candidates(
        self,
        candidates: List[HighlightCandidate],
    ) -> List[HighlightCandidate]:
        """Remove duplicate or very similar candidates"""
        if not candidates:
            return []

        # Sort by start time
        candidates.sort(key=lambda c: c.start_time)

        unique = [candidates[0]]

        for candidate in candidates[1:]:
            # Check if too similar to last unique candidate
            last = unique[-1]

            time_diff = abs(candidate.start_time - last.start_time)

            if time_diff > 5.0:  # At least 5 seconds apart
                unique.append(candidate)

        return unique
