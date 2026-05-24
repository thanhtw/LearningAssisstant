"""
FastAPI main application with CORS configuration and routes
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST, before other imports
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.routers import chat, session


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    print("🚀 Nova Backend starting up...")
    yield
    # Shutdown
    print("🛑 Nova Backend shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Nova Tutor Backend",
    description="AI Learning Assistant API built with FastAPI and LangGraph",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

if os.getenv("DEBUG") == "true":
    ALLOWED_ORIGINS.extend([
        "http://localhost:8080",
        "http://127.0.0.1:8000",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(chat.router, prefix="/api")


@app.get("/")
async def root():
    """Health check and API info"""
    return {
        "message": "Nova Tutor Backend",
        "status": "online",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "nova-backend",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if os.getenv("DEBUG") == "true" else None,
        },
    )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
    )
