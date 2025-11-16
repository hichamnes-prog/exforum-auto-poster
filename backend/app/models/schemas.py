"""
Pydantic schemas for API requests and responses
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingStep(str, Enum):
    """Processing pipeline steps"""
    UPLOADED = "uploaded"
    EXTRACTING_AUDIO = "extracting_audio"
    TRANSCRIBING = "transcribing"
    DETECTING_SCENES = "detecting_scenes"
    SCORING_HIGHLIGHTS = "scoring_highlights"
    GENERATING_CLIPS = "generating_clips"
    GENERATING_CAPTIONS = "generating_captions"
    COMPLETED = "completed"


class JobCreate(BaseModel):
    """Request to create a new job"""
    filename: str
    file_size: int
    duration: Optional[float] = None


class ProcessingProgress(BaseModel):
    """Processing progress information"""
    step: ProcessingStep
    progress: float = Field(ge=0, le=100, description="Progress percentage (0-100)")
    message: str
    current_clip: Optional[int] = None
    total_clips: Optional[int] = None


class Clip(BaseModel):
    """Clip metadata"""
    id: str
    job_id: str
    start_time: float
    end_time: float
    duration: float
    aspect_ratio: str
    score: float
    video_url: str
    caption_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    transcript: Optional[str] = None


class ClipResponse(BaseModel):
    """Response containing clip information"""
    clips: List[Clip]
    total: int


class Job(BaseModel):
    """Job information"""
    id: str
    status: JobStatus
    filename: str
    file_size: int
    duration: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    progress: Optional[ProcessingProgress] = None
    error: Optional[str] = None
    clips_count: int = 0
    video_url: Optional[str] = None


class JobResponse(BaseModel):
    """Response containing job information"""
    job: Job


class UploadResponse(BaseModel):
    """Response after file upload"""
    job_id: str
    filename: str
    file_size: int
    message: str


class TrimRequest(BaseModel):
    """Request to trim/re-export a clip"""
    start_time: float = Field(ge=0, description="New start time in seconds")
    end_time: float = Field(gt=0, description="New end time in seconds")
    aspect_ratio: Optional[str] = Field(None, description="Optional aspect ratio override")


class TranscriptWord(BaseModel):
    """Word-level transcript"""
    word: str
    start: float
    end: float
    confidence: Optional[float] = None


class TranscriptSegment(BaseModel):
    """Transcript segment"""
    text: str
    start: float
    end: float
    words: List[TranscriptWord] = []


class Transcript(BaseModel):
    """Full transcript"""
    segments: List[TranscriptSegment]
    language: str
    duration: float


class Scene(BaseModel):
    """Scene detection result"""
    start_time: float
    end_time: float
    duration: float
    frame_count: int


class HighlightCandidate(BaseModel):
    """Candidate highlight/clip"""
    start_time: float
    end_time: float
    duration: float
    score: float
    speech_density: float
    audio_energy: float
    scene_changes: int
    transcript: str


class JobState(BaseModel):
    """Internal job state for worker"""
    job_id: str
    video_path: str
    audio_path: Optional[str] = None
    transcript: Optional[Transcript] = None
    scenes: List[Scene] = []
    highlights: List[HighlightCandidate] = []
    clips: List[Clip] = []
    metadata: Dict = {}
