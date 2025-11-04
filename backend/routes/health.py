"""
Health check endpoints for monitoring service connectivity and status.
Provides endpoints to verify external service availability and basic metrics.
"""

import logging
import time
from typing import Dict, Any
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


async def check_ollama_health() -> Dict[str, Any]:
    """Check Ollama service connectivity and model availability."""
    # In demo mode, return healthy status without checking external service
    if settings.demo_mode:
        return {
            "status": "healthy",
            "message": "Demo mode - using mock responses",
            "models_count": 1
        }
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Check if Ollama is running
            response = await client.get(f"{settings.ollama_base}/api/tags")
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_available = any(
                    model.get("name", "").startswith(settings.model_name) 
                    for model in models
                )
                
                return {
                    "status": "healthy" if model_available else "degraded",
                    "message": f"Model {settings.model_name} {'available' if model_available else 'not found'}",
                    "models_count": len(models)
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"Ollama returned status {response.status_code}",
                    "models_count": 0
                }
                
    except httpx.TimeoutException:
        return {
            "status": "unhealthy",
            "message": "Ollama service timeout",
            "models_count": 0
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Ollama connection error: {str(e)}",
            "models_count": 0
        }


async def check_whisper_health() -> Dict[str, Any]:
    """Check Whisper service connectivity."""
    # In demo mode or when Whisper is disabled, return healthy status
    if settings.demo_mode or not getattr(settings, 'enable_whisper', True):
        return {
            "status": "healthy",
            "message": "Using browser speech recognition"
        }
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Check if Whisper service is running
            response = await client.get(f"{settings.whisper_base}/health")
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "message": "Whisper service available"
                }
            else:
                return {
                    "status": "healthy",  # Don't fail if Whisper is unavailable
                    "message": "Whisper unavailable, using browser STT"
                }
                
    except httpx.TimeoutException:
        return {
            "status": "healthy",  # Don't fail if Whisper is unavailable
            "message": "Whisper timeout, using browser STT"
        }
    except Exception as e:
        return {
            "status": "healthy",  # Don't fail if Whisper is unavailable
            "message": "Whisper unavailable, using browser STT"
        }





@router.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint.
    Returns overall system health and individual service status.
    """
    start_time = time.time()
    
    # Check external services
    ollama_health = await check_ollama_health()
    whisper_health = await check_whisper_health()
    
    # Determine overall health
    services_healthy = (
        ollama_health["status"] == "healthy" and 
        whisper_health["status"] in ["healthy", "degraded"]
    )
    
    overall_status = "healthy" if services_healthy else "unhealthy"
    
    response_time = round((time.time() - start_time) * 1000, 2)
    
    health_data = {
        "status": overall_status,
        "timestamp": time.time(),
        "response_time_ms": response_time,
        "services": {
            "ollama": ollama_health,
            "whisper": whisper_health
        },
        "configuration": {
            "ollama_base": settings.ollama_base,
            "whisper_base": settings.whisper_base,
            "model_name": settings.model_name
        }
    }
    
    # Return appropriate HTTP status
    status_code = 200 if services_healthy else 503
    
    logger.info(f"Health check completed: {overall_status} ({response_time}ms)")
    
    return JSONResponse(
        status_code=status_code,
        content=health_data
    )


@router.get("/health/ollama")
async def ollama_health_check():
    """Specific health check for Ollama service."""
    health_data = await check_ollama_health()
    status_code = 200 if health_data["status"] in ["healthy", "degraded"] else 503
    
    return JSONResponse(
        status_code=status_code,
        content=health_data
    )


@router.get("/health/whisper")
async def whisper_health_check():
    """Specific health check for Whisper service."""
    health_data = await check_whisper_health()
    status_code = 200 if health_data["status"] == "healthy" else 503
    
    return JSONResponse(
        status_code=status_code,
        content=health_data
    )





@router.get("/metrics")
async def basic_metrics():
    """
    Basic metrics endpoint for observability.
    Returns simple application metrics.
    """
    import psutil
    import os
    
    # Get system metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "application": {
            "name": "dhanvantri-chatbot",
            "version": "1.0.0",
            "uptime_seconds": time.time(),
            "process_id": os.getpid()
        },
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2)
        },
        "configuration": {
            "log_level": settings.log_level,
            "production_features": settings.enable_production_features,
            "supported_languages": ["en", "hi", "bn", "bho", "kn"],
            "max_concurrent_requests": settings.max_concurrent_requests,
            "request_timeout": settings.request_timeout
        }
    }


@router.get("/ready")
async def readiness_check():
    """
    Kubernetes-style readiness probe.
    Returns 200 if the service is ready to accept traffic.
    """
    # In demo mode, always return ready
    if settings.demo_mode:
        return {"status": "ready", "message": "Demo mode - service is ready"}
    
    # Check if critical services are available
    ollama_health = await check_ollama_health()
    
    if ollama_health["status"] in ["healthy", "degraded"]:
        return {"status": "ready", "message": "Service is ready to accept traffic"}
    else:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "message": "Critical services unavailable"}
        )


@router.get("/live")
async def liveness_check():
    """
    Kubernetes-style liveness probe.
    Returns 200 if the service is alive (basic health check).
    """
    return {
        "status": "alive",
        "timestamp": time.time(),
        "message": "Service is alive"
    }