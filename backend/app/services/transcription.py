"""
Transcription Service
Uses OpenAI Whisper and WhisperX for audio transcription
"""

import logging
from pathlib import Path
from typing import Optional

import torch
import whisper

from app.core.config import settings
from app.models.schemas import Transcript, TranscriptSegment, TranscriptWord

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Handles audio transcription using Whisper"""

    def __init__(self):
        self.model = None
        self.whisperx_available = False

        # Check if WhisperX is available
        try:
            import whisperx
            self.whisperx_available = True
            logger.info("WhisperX is available for word-level timestamps")
        except ImportError:
            logger.warning("WhisperX not available, using standard Whisper")

    def _load_model(self):
        """Load Whisper model (lazy loading)"""
        if self.model is None:
            logger.info(f"Loading Whisper model: {settings.whisper.model}")

            device = settings.whisper.device
            if device == "cuda" and not torch.cuda.is_available():
                logger.warning("CUDA not available, falling back to CPU")
                device = "cpu"

            self.model = whisper.load_model(
                settings.whisper.model,
                device=device,
            )

            logger.info(f"Whisper model loaded on {device}")

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> Transcript:
        """
        Transcribe audio file

        Args:
            audio_path: Path to audio file
            language: Language code (optional, auto-detect if None)

        Returns:
            Transcript object with segments and word-level timestamps
        """
        self._load_model()

        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Transcribing audio: {audio_path}")

        # Use WhisperX if available and enabled
        if self.whisperx_available and settings.whisper.use_whisperx:
            return self._transcribe_whisperx(str(audio_path), language)
        else:
            return self._transcribe_standard(str(audio_path), language)

    def _transcribe_standard(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> Transcript:
        """Transcribe using standard Whisper"""
        result = self.model.transcribe(
            audio_path,
            language=language or settings.whisper.language,
            verbose=False,
        )

        # Convert to our schema
        segments = []
        for seg in result["segments"]:
            # Standard Whisper doesn't have word-level timestamps
            words = []

            segment = TranscriptSegment(
                text=seg["text"].strip(),
                start=seg["start"],
                end=seg["end"],
                words=words,
            )
            segments.append(segment)

        transcript = Transcript(
            segments=segments,
            language=result.get("language", "unknown"),
            duration=segments[-1].end if segments else 0,
        )

        logger.info(
            f"Transcription complete: {len(segments)} segments, "
            f"language: {transcript.language}"
        )

        return transcript

    def _transcribe_whisperx(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> Transcript:
        """Transcribe using WhisperX for word-level timestamps"""
        import whisperx

        device = settings.whisper.device
        if device == "cuda" and not torch.cuda.is_available():
            device = "cpu"

        compute_type = settings.whisper.compute_type

        logger.info("Using WhisperX for word-level timestamps")

        # 1. Transcribe with Whisper
        result = self.model.transcribe(
            audio_path,
            language=language or settings.whisper.language,
            verbose=False,
        )

        detected_language = result.get("language", "en")

        # 2. Align whisper output for word-level timestamps
        if settings.whisper.align_model:
            try:
                model_a, metadata = whisperx.load_align_model(
                    language_code=detected_language,
                    device=device,
                )

                result = whisperx.align(
                    result["segments"],
                    model_a,
                    metadata,
                    audio_path,
                    device,
                    return_char_alignments=False,
                )

                # Clean up alignment model
                del model_a
                torch.cuda.empty_cache() if device == "cuda" else None

                logger.info("Word-level alignment complete")

            except Exception as e:
                logger.warning(f"Alignment failed, using segment-level only: {str(e)}")
                result = {"segments": result["segments"], "word_segments": []}

        # Convert to our schema
        segments = []
        for seg in result.get("segments", []):
            # Extract word-level timestamps if available
            words = []
            if "words" in seg:
                for word_data in seg["words"]:
                    word = TranscriptWord(
                        word=word_data.get("word", "").strip(),
                        start=word_data.get("start", seg["start"]),
                        end=word_data.get("end", seg["end"]),
                        confidence=word_data.get("score"),
                    )
                    words.append(word)

            segment = TranscriptSegment(
                text=seg["text"].strip(),
                start=seg["start"],
                end=seg["end"],
                words=words,
            )
            segments.append(segment)

        transcript = Transcript(
            segments=segments,
            language=detected_language,
            duration=segments[-1].end if segments else 0,
        )

        logger.info(
            f"WhisperX transcription complete: {len(segments)} segments, "
            f"language: {transcript.language}"
        )

        return transcript

    def generate_srt(self, transcript: Transcript, output_path: str) -> None:
        """
        Generate SRT subtitle file from transcript

        Args:
            transcript: Transcript object
            output_path: Output SRT file path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        def format_timestamp(seconds: float) -> str:
            """Format seconds to SRT timestamp (HH:MM:SS,mmm)"""
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(transcript.segments, 1):
                # SRT format:
                # 1
                # 00:00:00,000 --> 00:00:05,000
                # Subtitle text
                f.write(f"{i}\n")
                f.write(
                    f"{format_timestamp(segment.start)} --> "
                    f"{format_timestamp(segment.end)}\n"
                )
                f.write(f"{segment.text}\n\n")

        logger.info(f"Generated SRT file: {output_path}")
