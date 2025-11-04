"""
Main FastAPI application for Dhanvantri healthcare chatbot.
Provides REST API endpoints for multilingual medical conversations.
"""

import logging
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config import settings
from data.in_memory import initialize_storage
from routes.health import router as health_router
from routes.chat import router as chat_router
from routes.news import router as news_router


# Configure structured logging
def setup_logging():
    """Configure structured logging for the application."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown tasks."""
    # Startup
    logger.info("Starting Dhanvantri chatbot backend")
    
    # Load seed data
    try:
        initialize_storage()
        logger.info("Seed data loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load seed data: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Dhanvantri chatbot backend")


# Create FastAPI application
app = FastAPI(
    title="Dhanvantri Healthcare Chatbot",
    description="Multilingual healthcare education chatbot with voice capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(news_router, prefix="/api", tags=["news"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An internal server error occurred"
        }
    )


@app.get("/")
async def root():
    """Root endpoint providing basic API information."""
    return {
        "name": "Dhanvantri Healthcare Chatbot API",
        "version": "1.0.0",
        "status": "running",
        "supported_languages": ["en", "hi", "bn", "bho", "kn"]
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        reload=not settings.enable_production_features,
        workers=1 if not settings.enable_production_features else 4
    )