# Development Guide

This guide provides detailed instructions for developing ClipKit locally.

## Quick Start

### Using Docker (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Or use Make
make dev
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development (Without Docker)

#### Prerequisites

- Python 3.11+
- Node.js 20+
- Redis
- FFmpeg

#### Setup

```bash
# Run setup script
./scripts/dev-setup.sh

# Or manually:

# 1. Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
mkdir -p storage/{uploads,clips,captions,temp,jobs}

# 2. Frontend
cd frontend
npm install
```

#### Running Services

**Terminal 1 - Redis**
```bash
redis-server
```

**Terminal 2 - Backend**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 3 - Worker**
```bash
cd backend
source venv/bin/activate
celery -A app.worker.celery_app worker --loglevel=info
```

**Terminal 4 - Frontend**
```bash
cd frontend
npm run dev
```

## Project Structure

```
clipkit/
├── backend/                    # Python backend
│   ├── app/
│   │   ├── api/               # FastAPI endpoints
│   │   │   ├── upload.py      # Upload endpoint
│   │   │   └── jobs.py        # Job management endpoints
│   │   ├── core/              # Core configuration
│   │   │   └── config.py      # Settings management
│   │   ├── models/            # Data models
│   │   │   └── schemas.py     # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   │   ├── transcription.py       # Whisper transcription
│   │   │   ├── scene_detection.py     # PySceneDetect
│   │   │   ├── highlight_scorer.py    # Highlight scoring
│   │   │   ├── clip_generator.py      # Clip generation
│   │   │   ├── video_processor.py     # Video processing
│   │   │   └── job_manager.py         # Job state management
│   │   └── worker/            # Celery workers
│   │       ├── celery_app.py  # Celery configuration
│   │       └── tasks.py       # Processing tasks
│   ├── storage/               # File storage (gitignored)
│   ├── tests/                 # Tests
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   │   └── Layout.jsx     # Main layout
│   │   ├── pages/             # Page components
│   │   │   ├── HomePage.jsx   # Upload page
│   │   │   ├── JobsPage.jsx   # Jobs list
│   │   │   ├── JobDetailPage.jsx  # Job details
│   │   │   └── ClipsPage.jsx  # Clips viewer
│   │   ├── services/          # API client
│   │   │   └── api.js         # API functions
│   │   ├── App.jsx            # Root component
│   │   ├── main.jsx           # Entry point
│   │   └── index.css          # Global styles
│   ├── public/                # Static assets
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
├── scripts/                   # Utility scripts
├── clipkit.config.yaml        # Configuration
├── docker-compose.yml
├── Makefile
└── README.md
```

## Configuration

### Backend Configuration

Edit `clipkit.config.yaml` to customize:

```yaml
# Whisper model size
whisper:
  model: base  # tiny, base, small, medium, large
  device: cpu  # cpu or cuda

# Clip generation
clips:
  min_duration: 8
  max_duration: 60
  max_clips: 10

# Scene detection
scene_detection:
  threshold: 27.0  # Lower = more scenes detected

# Highlight scoring weights
highlight_scoring:
  speech_density_weight: 0.3
  audio_energy_weight: 0.25
  scene_change_weight: 0.2
```

### Environment Variables

Create `.env` file in project root:

```bash
# Backend
CLIPKIT_CONFIG=clipkit.config.yaml
CLIPKIT_WORKER__BROKER_URL=redis://localhost:6379/0

# Frontend
VITE_API_URL=http://localhost:8000/api
```

## Development Workflow

### Adding a New Feature

1. Create a feature branch
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make changes following the architecture:
   - Backend: Add service in `backend/app/services/`
   - API: Add endpoint in `backend/app/api/`
   - Frontend: Add component in `frontend/src/components/` or page

3. Test locally
   ```bash
   make test
   ```

4. Commit and push
   ```bash
   git add .
   git commit -m "feat: add my feature"
   git push origin feature/my-feature
   ```

### Backend Development

**Adding a New Service**

```python
# backend/app/services/my_service.py
from app.core.config import settings

class MyService:
    def process(self, input_data):
        # Implementation
        pass
```

**Adding an API Endpoint**

```python
# backend/app/api/my_endpoint.py
from fastapi import APIRouter
from app.services.my_service import MyService

router = APIRouter()

@router.post("/my-endpoint")
async def my_endpoint(data: dict):
    service = MyService()
    result = service.process(data)
    return result
```

**Register in main.py**

```python
from app.api import my_endpoint

app.include_router(my_endpoint.router, prefix="/api", tags=["my"])
```

### Frontend Development

**Creating a Component**

```jsx
// frontend/src/components/MyComponent.jsx
import { useState } from 'react';

function MyComponent({ prop1, prop2 }) {
  const [state, setState] = useState(null);

  return (
    <div className="card">
      {/* Component content */}
    </div>
  );
}

export default MyComponent;
```

**Adding an API Call**

```javascript
// frontend/src/services/api.js
export const myApiCall = async (data) => {
  const response = await api.post('/my-endpoint', data);
  return response.data;
};
```

## Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_transcription.py
```

### API Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Upload video
curl -X POST \
  -F "file=@test-video.mp4" \
  http://localhost:8000/api/upload

# Get jobs
curl http://localhost:8000/api/jobs
```

## Debugging

### Backend Debugging

Add breakpoints in your IDE or use:

```python
import pdb; pdb.set_trace()
```

### View Logs

```bash
# All services
make logs

# Specific service
make logs-backend
make logs-worker
make logs-frontend
```

### Access Containers

```bash
# Backend shell
make backend-shell

# Worker shell
make worker-shell

# Redis CLI
make redis-cli
```

## Performance Optimization

### CPU vs GPU

**CPU Mode** (default)
- Uses smaller Whisper models (tiny, base, small)
- Slower but works on any machine

**GPU Mode**
1. Install CUDA drivers and nvidia-docker
2. Update `clipkit.config.yaml`:
   ```yaml
   whisper:
     model: medium
     device: cuda
   ```
3. Uncomment GPU section in `docker-compose.yml`

### Optimization Tips

1. **Whisper Model Size**
   - `tiny`: Fastest, least accurate
   - `base`: Good balance (default)
   - `small`: Better accuracy
   - `medium`: Best for GPU
   - `large`: Best accuracy, slowest

2. **Scene Detection**
   - Higher threshold = fewer scenes = faster
   - Lower threshold = more scenes = slower

3. **Clip Generation**
   - Reduce `max_clips` for faster processing
   - Adjust `aspect_ratios` to generate fewer variants

## Common Issues

### Port Already in Use

```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in docker-compose.yml
```

### Redis Connection Error

```bash
# Check Redis is running
redis-cli ping

# Or start Redis
redis-server
```

### FFmpeg Not Found

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Check installation
ffmpeg -version
```

### Out of Memory

- Reduce Whisper model size
- Reduce `concurrent_workers` in config
- Process shorter videos
- Add more RAM/swap

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Whisper Documentation](https://github.com/openai/whisper)
- [PySceneDetect Documentation](https://scenedetect.com/)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
