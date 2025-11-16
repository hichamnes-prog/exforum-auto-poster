#!/bin/bash
# Development setup script for ClipKit

set -e

echo "🚀 Setting up ClipKit development environment..."

# Check for required tools
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed."; exit 1; }
command -v redis-cli >/dev/null 2>&1 || { echo "⚠️  Redis is not installed. You'll need Redis running for the worker."; }
command -v ffmpeg >/dev/null 2>&1 || { echo "❌ FFmpeg is required but not installed."; exit 1; }

echo "✅ Required tools found"

# Setup backend
echo ""
echo "📦 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Creating storage directories..."
mkdir -p storage/{uploads,clips,captions,temp,jobs}

cd ..

# Setup frontend
echo ""
echo "📦 Setting up frontend..."
cd frontend

echo "Installing Node dependencies..."
npm install

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Start Redis (if not using Docker): redis-server"
echo "2. Start backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "3. Start worker: cd backend && source venv/bin/activate && celery -A app.worker.celery_app worker --loglevel=info"
echo "4. Start frontend: cd frontend && npm run dev"
echo ""
echo "Or use Docker Compose: docker-compose up --build"
