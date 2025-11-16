"""
Configuration management for ClipKit
Loads settings from clipkit.config.yaml and environment variables
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class AspectRatio(BaseModel):
    """Aspect ratio configuration"""
    name: str
    ratio: str
    width: int
    height: int
    enabled: bool = True


class VideoConfig(BaseModel):
    """Video processing configuration"""
    max_upload_size_mb: int = 2000
    max_duration_hours: int = 2


class ClipsConfig(BaseModel):
    """Clip generation configuration"""
    min_duration: int = 8
    max_duration: int = 60
    target_duration: int = 30
    max_clips: int = 10
    aspect_ratios: List[AspectRatio] = []


class WhisperConfig(BaseModel):
    """Whisper transcription configuration"""
    model: str = "base"
    device: str = "cpu"
    language: Optional[str] = None
    use_whisperx: bool = True
    align_model: bool = True
    compute_type: str = "int8"
    batch_size: int = 16


class SceneDetectionConfig(BaseModel):
    """Scene detection configuration"""
    method: str = "content"
    threshold: float = 27.0
    min_scene_len: int = 15


class HighlightScoringConfig(BaseModel):
    """Highlight scoring configuration"""
    speech_density_weight: float = 0.3
    audio_energy_weight: float = 0.25
    scene_change_weight: float = 0.2
    sustained_speech_weight: float = 0.15
    duration_penalty_weight: float = 0.1
    min_speech_density: float = 1.5
    min_audio_energy: float = 0.3
    min_score: float = 0.4


class CaptionsConfig(BaseModel):
    """Caption configuration"""
    font_size: int = 24
    font_color: str = "white"
    font_outline_color: str = "black"
    font_outline_width: int = 2
    font_name: str = "Arial"
    position: str = "bottom"
    margin: int = 50
    max_words_per_caption: int = 10
    min_caption_duration: float = 0.5
    background: bool = True
    background_color: str = "black@0.5"


class StorageConfig(BaseModel):
    """Storage configuration"""
    base_path: str = "./storage"
    uploads_path: str = "./storage/uploads"
    clips_path: str = "./storage/clips"
    captions_path: str = "./storage/captions"
    temp_path: str = "./storage/temp"
    auto_cleanup_days: int = 7


class WorkerConfig(BaseModel):
    """Worker configuration"""
    broker_url: str = "redis://localhost:6379/0"
    result_backend: str = "redis://localhost:6379/0"
    task_time_limit: int = 3600
    concurrent_workers: int = 2


class FFmpegConfig(BaseModel):
    """FFmpeg configuration"""
    audio_codec: str = "pcm_s16le"
    audio_sample_rate: int = 16000
    video_codec: str = "libx264"
    video_preset: str = "medium"
    video_crf: int = 23
    audio_bitrate: str = "128k"
    hwaccel: Optional[str] = None


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class DevelopmentConfig(BaseModel):
    """Development configuration"""
    debug: bool = False
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    reload: bool = False


class Settings(BaseSettings):
    """Main application settings"""

    # App info
    app_name: str = "ClipKit"
    app_version: str = "0.1.0"

    # API settings
    api_prefix: str = "/api"

    # Configuration file path
    config_file: str = Field(default="clipkit.config.yaml", env="CLIPKIT_CONFIG")

    # Component configs (loaded from YAML)
    video: VideoConfig = Field(default_factory=VideoConfig)
    clips: ClipsConfig = Field(default_factory=ClipsConfig)
    whisper: WhisperConfig = Field(default_factory=WhisperConfig)
    scene_detection: SceneDetectionConfig = Field(default_factory=SceneDetectionConfig)
    highlight_scoring: HighlightScoringConfig = Field(default_factory=HighlightScoringConfig)
    captions: CaptionsConfig = Field(default_factory=CaptionsConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    worker: WorkerConfig = Field(default_factory=WorkerConfig)
    ffmpeg: FFmpegConfig = Field(default_factory=FFmpegConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    development: DevelopmentConfig = Field(default_factory=DevelopmentConfig)

    class Config:
        env_prefix = "CLIPKIT_"
        case_sensitive = False

    def load_config_file(self) -> None:
        """Load configuration from YAML file"""
        # Try multiple paths
        config_paths = [
            Path(self.config_file),
            Path(__file__).parent.parent.parent.parent / self.config_file,
            Path("/app") / self.config_file,
        ]

        config_data = None
        for config_path in config_paths:
            if config_path.exists():
                with open(config_path, "r") as f:
                    config_data = yaml.safe_load(f)
                print(f"Loaded configuration from {config_path}")
                break

        if not config_data:
            print(f"Warning: Config file not found, using defaults")
            return

        # Update settings from YAML
        if "video" in config_data:
            self.video = VideoConfig(**config_data["video"])
        if "clips" in config_data:
            self.clips = ClipsConfig(**config_data["clips"])
        if "whisper" in config_data:
            self.whisper = WhisperConfig(**config_data["whisper"])
        if "scene_detection" in config_data:
            self.scene_detection = SceneDetectionConfig(**config_data["scene_detection"])
        if "highlight_scoring" in config_data:
            self.highlight_scoring = HighlightScoringConfig(**config_data["highlight_scoring"])
        if "captions" in config_data:
            self.captions = CaptionsConfig(**config_data["captions"])
        if "storage" in config_data:
            self.storage = StorageConfig(**config_data["storage"])
        if "worker" in config_data:
            self.worker = WorkerConfig(**config_data["worker"])
        if "ffmpeg" in config_data:
            self.ffmpeg = FFmpegConfig(**config_data["ffmpeg"])
        if "logging" in config_data:
            self.logging = LoggingConfig(**config_data["logging"])
        if "development" in config_data:
            self.development = DevelopmentConfig(**config_data["development"])

    def ensure_storage_paths(self) -> None:
        """Ensure storage directories exist"""
        paths = [
            self.storage.base_path,
            self.storage.uploads_path,
            self.storage.clips_path,
            self.storage.captions_path,
            self.storage.temp_path,
        ]
        for path in paths:
            Path(path).mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.load_config_file()
settings.ensure_storage_paths()
