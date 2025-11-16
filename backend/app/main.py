"""
ClipKit FastAPI Application
Main entry point for the backend API
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import jobs, upload
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=settings.logging.level,
    format=settings.logging.format,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Storage path: {settings.storage.base_path}")

    # Ensure storage directories exist
    settings.ensure_storage_paths()

    yield

    logger.info(f"Shutting down {settings.app_name}")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-assisted short-video clipper",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.development.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving videos and clips
app.mount(
    "/storage",
    StaticFiles(directory=settings.storage.base_path),
    name="storage",
)

# Include API routers
app.include_router(upload.router, prefix=settings.api_prefix, tags=["upload"])
app.include_router(jobs.router, prefix=settings.api_prefix, tags=["jobs"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.development.reload,
    )
