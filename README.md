# ClipKit 🎬

**Open-source AI-assisted short-video clipper**

ClipKit is a self-hostable web application that automatically transforms long videos into social-ready short clips with AI-generated captions. Perfect for content creators, marketers, and anyone who needs to repurpose long-form video content.

## Features

- 🎥 **Automatic Clip Generation**: Upload a video and get multiple 8-60s clips automatically
- 🗣️ **AI Transcription**: Powered by OpenAI Whisper for accurate captions
- 🎯 **Smart Highlights**: Automatic detection of interesting moments using scene detection and audio analysis
- ✂️ **Clip Editor**: Preview and adjust clip start/end times with precision
- 📱 **Multiple Formats**: Export in vertical (9:16) and landscape (16:9) for different platforms
- 💬 **Captions**: Auto-generated SRT files and burned-in captions
- 🐳 **Self-Hostable**: Run locally with Docker Compose
- 💻 **CPU & GPU Support**: Works on CPU-only systems with optional GPU acceleration

## Quick Start

### Prerequisites

- Docker and Docker Compose
- 8GB+ RAM recommended
- (Optional) NVIDIA GPU with CUDA for faster processing

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/clipkit.git
cd clipkit
```

2. **Start the application**
```bash
docker-compose up --build
```

3. **Access the UI**
- Open http://localhost:3000 in your browser
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Development Mode

**Backend (Python/FastAPI)**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (React/Vite)**
```bash
cd frontend
npm install
npm run dev
```

**Worker (Celery)**
```bash
cd backend
celery -A app.worker.celery_app worker --loglevel=info
```

**Redis**
```bash
docker run -p 6379:6379 redis:alpine
```

## Usage

1. **Upload a Video**: Drag and drop or select a video file (up to 2 hours)
2. **Generate Clips**: Click "Generate Clips" and wait for processing
3. **Preview & Edit**: Review generated clips, adjust timing if needed
4. **Download**: Get your clips with SRT caption files

## Architecture

```
clipkit/
├── backend/           # FastAPI backend + Celery workers
│   ├── app/
│   │   ├── api/       # REST API endpoints
│   │   ├── worker/    # Background job processing
│   │   ├── core/      # Configuration and utilities
│   │   └── services/  # Business logic (transcription, clipping, etc.)
│   ├── storage/       # Local file storage (videos, clips, captions)
│   └── tests/         # Unit tests
├── frontend/          # React + Vite UI
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── public/
├── docker-compose.yml
└── clipkit.config.yaml
```

## Configuration

Edit `clipkit.config.yaml` to customize:

- **Clip duration**: Min/max clip length
- **Highlight thresholds**: Tune what counts as "interesting"
- **Output formats**: Aspect ratios (9:16, 16:9, 1:1)
- **Transcription**: Whisper model size (tiny, base, small, medium, large)
- **Scene detection**: Sensitivity settings

## CPU vs GPU Mode

**CPU Mode (Default)**
Uses `whisper.cpp` or smaller Whisper models for CPU-only environments.

**GPU Mode**
For faster processing with NVIDIA GPUs:

1. Edit `docker-compose.yml`:
```yaml
services:
  worker:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

2. Set in `clipkit.config.yaml`:
```yaml
whisper:
  model: medium  # or large
  device: cuda
```

## Technology Stack

- **Backend**: Python 3.11, FastAPI
- **Worker**: Celery, Redis
- **AI/ML**: OpenAI Whisper, WhisperX, PySceneDetect
- **Video**: FFmpeg
- **Frontend**: React 18, Vite, Tailwind CSS
- **Infrastructure**: Docker, Docker Compose

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.

**Key Endpoints:**
- `POST /api/upload` - Upload video
- `POST /api/jobs/{id}/generate` - Start clip generation
- `GET /api/jobs/{id}` - Get job status
- `GET /api/jobs/{id}/clips` - List generated clips
- `POST /api/jobs/{id}/clips/{clip_id}/trim` - Adjust clip timing

## Performance

Processing time varies based on:
- Video length
- Hardware (CPU vs GPU)
- Whisper model size
- Number of clips generated

**Typical benchmarks:**
- 10-min video on CPU (Whisper base): ~5-10 minutes
- 10-min video on GPU (Whisper medium): ~2-3 minutes

## Roadmap

- [ ] Multi-language support
- [ ] Advanced templates and overlays
- [ ] Batch processing
- [ ] Cloud storage integration (S3, MinIO)
- [ ] Face detection for smart cropping
- [ ] Speaker diarization
- [ ] Social media platform presets

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [WhisperX](https://github.com/m-bain/whisperX) - Word-level timestamps
- [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) - Scene detection
- [FFmpeg](https://ffmpeg.org/) - Video processing

## Support

- 📖 [Documentation](https://github.com/yourusername/clipkit/wiki)
- 🐛 [Issue Tracker](https://github.com/yourusername/clipkit/issues)
- 💬 [Discussions](https://github.com/yourusername/clipkit/discussions)

---

Built with ❤️ by the ClipKit community
