"""
Configuration module for Dhanvantri chatbot backend.
Provides typed configuration management using Pydantic settings.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Ollama Configuration
    ollama_base: str = "http://localhost:11434"
    model_name: str = "alibayram/medgemma:4b"
    
    # Whisper Configuration  
    whisper_base: str = "http://localhost:5001"
    
    # Application Configuration
    port: int = int(os.getenv("PORT", "8000"))  # Render sets PORT env var
    host: str = "0.0.0.0"
    log_level: str = "INFO"
    enable_production_features: bool = False
    
    # Render-specific configuration
    render_external_hostname: Optional[str] = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    render_service_name: Optional[str] = os.getenv("RENDER_SERVICE_NAME")
    
    # CORS Configuration - dynamically set for Render
    cors_origins: List[str] = [
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://localhost:3002", 
        "http://localhost:5173",
        "http://localhost:8080"
    ]
    
    # Security Configuration
    max_request_size: str = "10MB"
    request_timeout: int = 30
    max_concurrent_requests: int = 100
    
    # Feature Flags
    enable_voice_features: bool = True
    enable_translation: bool = True
    enable_medical_disclaimer: bool = True
    enable_emergency_detection: bool = True
    demo_mode: bool = os.getenv("DEMO_MODE", "false").lower() == "true"
    
    # Model Configuration
    model_temperature: float = 0.7
    model_max_tokens: int = 512
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from environment variable if provided as string."""
        origins = []
        
        # Handle string format (comma-separated)
        if isinstance(self.cors_origins, str):
            origins = [origin.strip() for origin in self.cors_origins.split(",")]
        else:
            origins = self.cors_origins.copy()
        
        # Add Render hostname if available
        if self.render_external_hostname:
            render_urls = [
                f"https://{self.render_external_hostname}",
                f"http://{self.render_external_hostname}"
            ]
            origins.extend(render_urls)
        
        # Add environment-specific CORS origins
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            env_origins = [origin.strip() for origin in cors_env.split(",")]
            origins.extend(env_origins)
        
        return list(set(origins))  # Remove duplicates


# Global settings instance
settings = Settings()