# ClipKit Application Preview

## 🎬 What You've Built

ClipKit is a complete, production-ready AI-powered video clipper that automatically transforms long videos into social-ready short clips with captions.

---

## 📂 Project Architecture

```
clipkit/
├── 📄 README.md                    # User documentation
├── 📄 DEVELOPMENT.md              # Developer guide
├── 📄 CONTRIBUTING.md             # Contribution guidelines
├── 📄 LICENSE                     # MIT License
├── 📄 Makefile                    # Convenience commands
├── 📄 docker-compose.yml          # Docker orchestration
├── 📄 clipkit.config.yaml         # Application configuration
│
├── 🐍 backend/                    # Python FastAPI Backend
│   ├── 📄 Dockerfile
│   ├── 📄 requirements.txt
│   └── app/
│       ├── 🌐 api/                # REST API Endpoints
│       │   ├── upload.py          # Video upload endpoint
│       │   └── jobs.py            # Job management endpoints
│       │
│       ├── ⚙️ core/               # Core Configuration
│       │   └── config.py          # Settings & YAML loader
│       │
│       ├── 📦 models/             # Data Models
│       │   └── schemas.py         # Pydantic schemas
│       │
│       ├── 🔧 services/           # Business Logic
│       │   ├── transcription.py       # Whisper/WhisperX
│       │   ├── scene_detection.py     # PySceneDetect
│       │   ├── highlight_scorer.py    # AI highlight scoring
│       │   ├── clip_generator.py      # FFmpeg clip creation
│       │   ├── video_processor.py     # Video preprocessing
│       │   └── job_manager.py         # Job state management
│       │
│       ├── 👷 worker/             # Background Processing
│       │   ├── celery_app.py      # Celery configuration
│       │   └── tasks.py           # Processing pipeline
│       │
│       └── main.py                # FastAPI application
│
├── ⚛️ frontend/                   # React Frontend
│   ├── 📄 Dockerfile
│   ├── 📄 nginx.conf
│   ├── 📄 package.json
│   ├── 📄 vite.config.js
│   ├── 📄 tailwind.config.js
│   └── src/
│       ├── 📱 pages/              # Page Components
│       │   ├── HomePage.jsx           # Upload & landing
│       │   ├── JobsPage.jsx           # Jobs list
│       │   ├── JobDetailPage.jsx      # Job details & progress
│       │   └── ClipsPage.jsx          # Clip gallery & editor
│       │
│       ├── 🧩 components/         # Reusable Components
│       │   └── Layout.jsx             # App layout & nav
│       │
│       ├── 🔌 services/           # API Integration
│       │   └── api.js                 # Axios API client
│       │
│       ├── App.jsx                # Root component
│       ├── main.jsx               # Entry point
│       └── index.css              # Global styles
│
└── 📜 scripts/                    # Utility Scripts
    ├── dev-setup.sh               # Development setup
    └── test-api.sh                # API testing

```

---

## 🚀 Quick Start Commands

```bash
# Using Docker (Recommended)
docker-compose up --build

# Using Make
make dev              # Start all services
make logs             # View logs
make down             # Stop services

# Manual Development
./scripts/dev-setup.sh
```

**Access Points:**
- 🌐 Frontend: http://localhost:3000
- 🔧 Backend API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs

---

## 🎨 User Interface Flow

### 1️⃣ Home Page (Upload)
```
┌─────────────────────────────────────────────────────┐
│  🎬 ClipKit - AI-Powered Video Clipper             │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  📤 Upload Video                             │  │
│  │                                               │  │
│  │  ┌────────────────────────────────────────┐ │  │
│  │  │                                         │ │  │
│  │  │     📁  Drop your video here           │ │  │
│  │  │          or click to browse            │ │  │
│  │  │                                         │ │  │
│  │  │     MP4, MOV, AVI, MKV (max 2GB)      │ │  │
│  │  │                                         │ │  │
│  │  └────────────────────────────────────────┘ │  │
│  │                                               │  │
│  │  [✨ Generate Clips]  [Cancel]               │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  Features:                                           │
│  ✨ AI-Powered      🎞️ Multi-Format    📝 Captions │
└─────────────────────────────────────────────────────┘
```

**Features:**
- Drag & drop upload
- File type validation
- Size validation (2GB max)
- Instant upload with progress bar
- Auto-starts processing

---

### 2️⃣ Jobs Page
```
┌─────────────────────────────────────────────────────┐
│  Your Jobs                    [Upload New Video]    │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ 🎬 my-video.mp4                              │  │
│  │ Created: 2025-11-16 10:30                    │  │
│  │ Duration: 5:30 | 3 clips                     │  │
│  │                                               │  │
│  │ Processing... 75%                             │  │
│  │ ████████████████░░░░░░░░                     │  │
│  │ Generating video clips...                     │  │
│  │                                               │  │
│  │                              [✓ Processing]   │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ 🎬 presentation.mp4                          │  │
│  │ Created: 2025-11-15 14:20                    │  │
│  │ Duration: 10:15 | 5 clips                    │  │
│  │                                               │  │
│  │                              [✓ Completed]    │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Features:**
- Real-time progress tracking
- Auto-refresh every 3 seconds
- Job status indicators
- Click to view details

---

### 3️⃣ Job Detail Page
```
┌─────────────────────────────────────────────────────┐
│  ← Back to Jobs                                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  my-video.mp4                      [✓ Completed]    │
│  Created: 2025-11-16 10:30                          │
│  Size: 150 MB | Duration: 5:30                      │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ Generated Clips (3)          [🎬 View Clips] │  │
│  │                                               │  │
│  │ ✅ Processing complete! 3 clips have been    │  │
│  │    generated and are ready to download.      │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  Original Video:                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │                                               │  │
│  │          [▶️ Video Player]                   │  │
│  │                                               │  │
│  │     ─────────────○──────────   0:30 / 5:30  │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Features:**
- Video metadata display
- Processing progress with steps
- Original video preview
- Direct link to clips

---

### 4️⃣ Clips Gallery
```
┌─────────────────────────────────────────────────────┐
│  ← Back to Job          Generated Clips (6)         │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Vertical (Stories/Reels) - 3 clips                 │
│  ┌──────┐  ┌──────┐  ┌──────┐                      │
│  │ ▶️   │  │ ▶️   │  │ ▶️   │                      │
│  │      │  │      │  │      │                      │
│  │ Clip │  │ Clip │  │ Clip │                      │
│  │  1   │  │  2   │  │  3   │                      │
│  │      │  │      │  │      │                      │
│  └──────┘  └──────┘  └──────┘                      │
│   0:15-0:45  1:20-1:50  3:10-3:40                   │
│   Score: 85% Score: 78% Score: 72%                  │
│   [⬇️][✂️]  [⬇️][✂️]  [⬇️][✂️]                     │
│   Download SRT | Download SRT | Download SRT         │
│                                                      │
│  Landscape (YouTube) - 3 clips                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐              │
│  │  ▶️     │ │  ▶️     │ │  ▶️     │              │
│  │  Clip 1 │ │  Clip 2 │ │  Clip 3 │              │
│  └─────────┘ └─────────┘ └─────────┘              │
│   [⬇️][✂️]   [⬇️][✂️]   [⬇️][✂️]                  │
│                                                      │
└─────────────────────────────────────────────────────┘

✂️ Trim Dialog (when clicked):
┌─────────────────────────────────────┐
│  Trim Clip                      [×] │
├─────────────────────────────────────┤
│  ┌───────────────────────────────┐ │
│  │     [▶️ Video Preview]       │ │
│  └───────────────────────────────┘ │
│                                     │
│  Start Time: [0.15] seconds        │
│  End Time:   [0.45] seconds        │
│  New duration: 0:00:30              │
│                                     │
│  [Apply Trim]  [Cancel]            │
└─────────────────────────────────────┘
```

**Features:**
- Clips organized by aspect ratio
- Video player for each clip
- Download video + SRT captions
- Trim/re-export functionality
- Quality score display
- Transcript preview

---

## 🔧 Configuration (clipkit.config.yaml)

```yaml
# Video Settings
video:
  max_upload_size_mb: 2000
  max_duration_hours: 2

# Clip Generation
clips:
  min_duration: 8        # Minimum 8 seconds
  max_duration: 60       # Maximum 60 seconds
  max_clips: 10          # Generate up to 10 clips

  aspect_ratios:
    - name: "vertical"   # TikTok, Reels, Stories
      ratio: "9:16"
      width: 1080
      height: 1920
    - name: "landscape"  # YouTube, traditional
      ratio: "16:9"
      width: 1920
      height: 1080

# AI Transcription (Whisper)
whisper:
  model: "base"          # tiny|base|small|medium|large
  device: "cpu"          # cpu|cuda
  use_whisperx: true     # Word-level timestamps

# Highlight Scoring Algorithm
highlight_scoring:
  speech_density_weight: 0.3      # 30% - Words per second
  audio_energy_weight: 0.25       # 25% - Audio loudness
  scene_change_weight: 0.2        # 20% - Visual interest
  sustained_speech_weight: 0.15   # 15% - Continuous talking
  duration_penalty_weight: 0.1    # 10% - Length preference
```

---

## 🔄 Processing Pipeline

```
1. Upload Video
   ↓
2. Extract Audio (FFmpeg)
   ↓
3. Transcribe (Whisper/WhisperX)
   → Word-level timestamps
   → Language detection
   ↓
4. Detect Scenes (PySceneDetect)
   → Scene boundaries
   → Shot changes
   ↓
5. Score Highlights
   → Speech density analysis
   → Audio energy peaks
   → Scene change frequency
   → Weighted scoring algorithm
   ↓
6. Generate Clips (FFmpeg)
   → Multi-aspect ratio export
   → Smart cropping/scaling
   → Caption burning
   ↓
7. Generate SRT Captions
   → Time-aligned subtitles
   → Per-clip SRT files
   ↓
8. Complete ✅
   → Clips ready for download
```

---

## 📊 API Endpoints

```
POST   /api/upload                    # Upload video
GET    /api/jobs                      # List all jobs
GET    /api/jobs/{id}                 # Get job details
POST   /api/jobs/{id}/generate        # Start processing
GET    /api/jobs/{id}/clips           # List clips
GET    /api/jobs/{id}/clips/{clip_id} # Get clip details
POST   /api/jobs/{id}/clips/{clip_id}/trim  # Trim clip
DELETE /api/jobs/{id}                 # Delete job

GET    /health                        # Health check
GET    /                              # API info
GET    /docs                          # Swagger UI
```

---

## 🛠️ Technology Stack

**Backend:**
- Python 3.11
- FastAPI (REST API)
- Celery (Background tasks)
- Redis (Message broker)
- OpenAI Whisper (Transcription)
- WhisperX (Word timestamps)
- PySceneDetect (Scene detection)
- Librosa (Audio analysis)
- FFmpeg (Video processing)

**Frontend:**
- React 18
- Vite (Build tool)
- Tailwind CSS (Styling)
- React Router (Navigation)
- Axios (HTTP client)
- Lucide Icons

**Infrastructure:**
- Docker & Docker Compose
- Nginx (Frontend serving)
- File-based storage

---

## 📈 Performance

**CPU Processing (Base Model):**
- 10-minute video: ~5-10 minutes
- Model download: ~150MB (one-time)
- Memory usage: ~2-4GB

**GPU Processing (Medium Model):**
- 10-minute video: ~2-3 minutes
- Requires: CUDA-capable GPU
- Memory usage: ~4-6GB

---

## 🎯 Use Cases

1. **Content Creators**
   - Repurpose long videos into shorts
   - Auto-generate social media clips
   - Save hours of manual editing

2. **Marketing Teams**
   - Extract highlights from webinars
   - Create promotional clips
   - Generate multiple format variants

3. **Educators**
   - Create bite-sized lesson clips
   - Extract key moments from lectures
   - Add automatic captions

4. **Podcasters**
   - Generate audiogram-style clips
   - Extract best moments
   - Create shareable snippets

---

## 🔐 Privacy & Self-Hosting

✅ **100% Self-Hosted**
- All processing happens locally
- No data sent to external services
- Full control over your content

✅ **Open Source (MIT)**
- Free to use and modify
- No vendor lock-in
- Community-driven development

---

## 📦 What's Included

✅ Complete backend API
✅ Modern React frontend
✅ Docker deployment
✅ Configuration system
✅ Job management
✅ Progress tracking
✅ Multi-format export
✅ Caption generation
✅ Clip editing
✅ Comprehensive documentation
✅ Development scripts
✅ Example configuration

---

## 🚀 Next Steps

1. **Start the application:**
   ```bash
   docker-compose up --build
   ```

2. **Upload a test video** (5-15 min recommended)

3. **Watch the AI work:**
   - Transcription
   - Scene detection
   - Highlight scoring
   - Clip generation

4. **Download your clips!**

5. **Customize:**
   - Edit `clipkit.config.yaml`
   - Adjust scoring weights
   - Change clip durations
   - Add more aspect ratios

---

## 📝 Files Summary

**Total:** 49 files, ~5,500 lines of code

**Backend:** 19 Python files
**Frontend:** 12 JavaScript/React files
**Config:** 8 configuration files
**Docs:** 4 documentation files
**Scripts:** 2 utility scripts
**Infrastructure:** 4 Docker/compose files

---

**🎉 ClipKit is ready to use!**

Start with: `docker-compose up --build`
Visit: http://localhost:3000
