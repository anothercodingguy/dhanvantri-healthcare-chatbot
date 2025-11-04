"""
Ollama client for MedGemma-4B integration.
Provides chat functionality with retry logic and error handling.
"""

import requests
import time
import logging
from typing import Optional, Dict, Any
from config import settings

logger = logging.getLogger(__name__)


class OllamaError(Exception):
    """Custom exception for Ollama service errors."""
    pass


class OllamaClient:
    """Client for interacting with local Ollama service."""
    
    def __init__(self, base_url: str = None, model_name: str = None):
        self.base_url = base_url or settings.ollama_base
        self.model_name = model_name or settings.model_name
        self.chat_url = f"{self.base_url}/api/chat"
        self.generate_url = f"{self.base_url}/api/generate"
        
    def _make_request(self, url: str, payload: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        for attempt in range(max_retries):
            try:
                # Use longer timeout for complex medical analysis
                timeout = 60 if "MEDICAL IMAGE ANALYSIS" in str(payload.get('messages', [])) else 30
                response = requests.post(
                    url,
                    json=payload,
                    timeout=timeout,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Ollama connection failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise OllamaError(f"Failed to connect to Ollama service at {self.base_url}")
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except requests.exceptions.Timeout as e:
                logger.warning(f"Ollama request timeout (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise OllamaError("Ollama service request timed out")
                time.sleep(2 ** attempt)
                
            except requests.exceptions.HTTPError as e:
                logger.error(f"Ollama HTTP error: {e}")
                raise OllamaError(f"Ollama service returned error: {e}")
                
            except Exception as e:
                logger.error(f"Unexpected error communicating with Ollama: {e}")
                raise OllamaError(f"Unexpected error: {e}")
    
    def chat(self, prompt: str, system_prompt: str = None, temperature: float = 0.1) -> str:
        """
        Send a chat message to MedGemma-4B and get response.
        
        Args:
            prompt: User's message/question
            system_prompt: System prompt for medical context
            temperature: Response randomness (0.0-1.0, lower = more deterministic)
            
        Returns:
            str: The model's response text
            
        Raises:
            OllamaError: If the service is unavailable or returns an error
        """
        try:
            # Construct system prompt for medical conversations
            if system_prompt is None:
                system_prompt = self._construct_medical_system_prompt()
            
            # Prepare chat payload
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user", 
                "content": prompt
            })
            
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            logger.info(f"Sending chat request to Ollama with model {self.model_name}")
            response_data = self._make_request(self.chat_url, payload)
            
            # Extract response text
            if "message" in response_data and "content" in response_data["message"]:
                response_text = response_data["message"]["content"].strip()
                logger.info("Successfully received response from Ollama")
                return response_text
            else:
                logger.error(f"Unexpected response format from Ollama: {response_data}")
                raise OllamaError("Invalid response format from Ollama service")
                
        except OllamaError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in chat method: {e}")
            raise OllamaError(f"Chat request failed: {e}")
    
    def _construct_medical_system_prompt(self) -> str:
        """Construct system prompt for medical conversations."""
        return """You are Dhanvantri, a helpful medical education assistant. You provide evidence-based health information to help users understand medical topics.

Guidelines:
- Provide accurate, evidence-based medical information
- Use clear, simple language appropriate for general audiences
- Focus on education and general health awareness
- Always emphasize that your information is for educational purposes only
- Recommend consulting healthcare professionals for personal medical advice
- Be empathetic and supportive in your responses
- If you're uncertain about something, clearly state the limitations of your knowledge

Remember: You are an educational tool, not a replacement for professional medical consultation."""

    def health_check(self) -> Dict[str, Any]:
        """
        Check if Ollama service is available and responsive.
        
        Returns:
            Dict with health status information
        """
        try:
            # Simple health check using the generate endpoint
            payload = {
                "model": self.model_name,
                "prompt": "Hello",
                "stream": False,
                "options": {"max_tokens": 5}
            }
            
            response_data = self._make_request(self.generate_url, payload, max_retries=1)
            
            return {
                "status": "healthy",
                "model": self.model_name,
                "base_url": self.base_url,
                "response_received": True
            }
            
        except Exception as e:
            return {
                "status": "unhealthy", 
                "model": self.model_name,
                "base_url": self.base_url,
                "error": str(e)
            }


# Global client instance
ollama_client = OllamaClient()


def ollama_chat(prompt: str, system_prompt: str = None, temperature: float = 0.1) -> str:
    """
    Convenience function for chat requests.
    
    Args:
        prompt: User's message/question
        system_prompt: Optional system prompt override
        temperature: Response randomness
        
    Returns:
        str: The model's response
        
    Raises:
        OllamaError: If the service is unavailable
    """
    return ollama_client.chat(prompt, system_prompt, temperature)