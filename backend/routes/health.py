"""
Health check endpoints for monitoring service connectivity and status.
Provides endpoints to verify external service availability and basic metrics.
"""

import logging
import time
from typing import Dict, Any
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from config import settings
# Import Groq client to checking health
from services.groq_client import groq_client

logger = logging.getLogger(__name__)
router = APIRouter()


async def check_groq_health() -> Dict[str, Any]:
    """Check Groq API connectivity."""
    # In demo mode, return healthy status without checking external service
    if settings.demo_mode:
        return {
            "status": "healthy",
            "message": "Demo mode - using mock responses",
            "provider": "Groq (Mock)"
        }
    
    try:
        # We can perform a lightweight check, e.g. listing models or a simple chat
        # Groq client doesn't have a specific ping, but we can try a simple chat
        # or just check if API key is present. A real check is better.
        # Let's try to list models if client exposes it, or just send a tiny prompt.
        # groq_client in services doesn't expose list_models, but we can add or just use chat.
        
        # Simple prompt
        try:
             # Minimal token usage check
             await groq_client.chat("ping", temperature=0.0)
             return {
                 "status": "healthy",
                 "message": "Groq API available",
                 "provider": "Groq"
             }
        except Exception as e:
             return {
                 "status": "unhealthy",
                 "message": f"Groq API error: {str(e)}",
                 "provider": "Groq"
             }
                
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Health check error: {str(e)}",
            "provider": "Groq"
        }


@router.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint.
    Returns overall system health and individual service status.
    """
    start_time = time.time()
    
    # Check external services
    groq_health = await check_groq_health()
    
    # Determine overall health
    services_healthy = (
        groq_health["status"] == "healthy"
    )
    
    overall_status = "healthy" if services_healthy else "unhealthy"
    
    response_time = round((time.time() - start_time) * 1000, 2)
    
    health_data = {
        "status": overall_status,
        "timestamp": time.time(),
        "response_time_ms": response_time,
        "services": {
            "llm": groq_health,
            "stt": groq_health # Groq handles both
        },
        "configuration": {
            "model_name": settings.model_name,
            "stt_model": settings.stt_model
        }
    }
    
    # Return appropriate HTTP status
    status_code = 200 if services_healthy else 503
    
    logger.info(f"Health check completed: {overall_status} ({response_time}ms)")
    
    return JSONResponse(
        status_code=status_code,
        content=health_data
    )


@router.get("/health/llm")
async def llm_health_check():
    """Specific health check for LLM service."""
    health_data = await check_groq_health()
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
    groq_health = await check_groq_health()
    
    if groq_health["status"] == "healthy":
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