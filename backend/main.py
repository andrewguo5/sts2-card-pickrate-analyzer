"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from config import settings
from database import engine, Base
from routers import auth, runs, analytics, steam
from card_metadata import load_card_metadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Load card metadata from Spire Codex on startup
logger.info("Initializing card metadata cache...")
load_card_metadata()

# Initialize FastAPI app
app = FastAPI(
    title="STS2 Analytics API",
    description="Slay the Spire 2 run history analytics platform",
    version="1.0.0"
)

# CORS middleware (allow frontend to access API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(runs.router)
app.include_router(analytics.router)
app.include_router(steam.router)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "STS2 Analytics API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "runs": "/api/runs",
            "analytics": "/api/analytics",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True  # Auto-reload on code changes
    )
