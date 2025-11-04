"""
Whisper client for speech-to-text and translation functionality.
Handles audio transcription and language translation for multilingual support.
"""

import requests
import base64
import logging
from typing import Optional, Dict, Any, List
from config import settings

logger = logging.getLogger(__name__)


class WhisperError(Exception):
    """Custom exception for Whisper service errors."""
    pass


class WhisperClient:
    """Client for interacting with local Whisper service."""
    
    # Supported languages for the Dhanvantri system
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'hi': 'Hindi', 
        'bn': 'Bengali',
        'bho': 'Bhojpuri',
        'kn': 'Kannada'
    }
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.whisper_base
        self.transcribe_url = f"{self.base_url}/transcribe"
        self.translate_url = f"{self.base_url}/translate"
        
    def _make_request(self, url: str, data: Dict[str, Any] = None, files: Dict[str, Any] = None, max_retries: int = 2) -> Dict[str, Any]:
        """Make HTTP request with basic retry logic."""
        for attempt in range(max_retries):
            try:
                if files:
                    response = requests.post(url, data=data, files=files, timeout=60)
                else:
                    response = requests.post(
                        url, 
                        json=data, 
                        timeout=30,
                        headers={"Content-Type": "application/json"}
                    )
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Whisper connection failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise WhisperError(f"Failed to connect to Whisper service at {self.base_url}")
                    
            except requests.exceptions.Timeout as e:
                logger.warning(f"Whisper request timeout (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise WhisperError("Whisper service request timed out")
                    
            except requests.exceptions.HTTPError as e:
                logger.error(f"Whisper HTTP error: {e}")
                if e.response.status_code == 400:
                    try:
                        error_detail = e.response.json()
                        raise WhisperError(f"Whisper service error: {error_detail.get('error', str(e))}")
                    except:
                        raise WhisperError(f"Whisper service returned bad request: {e}")
                else:
                    raise WhisperError(f"Whisper service returned error: {e}")
                    
            except Exception as e:
                logger.error(f"Unexpected error communicating with Whisper: {e}")
                if attempt == max_retries - 1:
                    raise WhisperError(f"Unexpected error: {e}")
    
    def transcribe_audio_bytes(self, audio_bytes: bytes, language: str = None) -> Dict[str, Any]:
        """
        Transcribe audio bytes to text using Whisper service.
        
        Args:
            audio_bytes: Raw audio data in bytes
            language: Optional language hint (ISO 639-1 code)
            
        Returns:
            Dict containing:
                - text: Transcribed text
                - language: Detected language code
                - confidence: Confidence score (0.0-1.0)
                
        Raises:
            WhisperError: If transcription fails or service is unavailable
        """
        try:
            # Validate language if provided
            if language and language not in self.SUPPORTED_LANGUAGES:
                logger.warning(f"Unsupported language hint: {language}. Proceeding without language hint.")
                language = None
            
            # Prepare multipart form data
            files = {
                'audio': ('audio.wav', audio_bytes, 'audio/wav')
            }
            
            data = {}
            if language:
                data['language'] = language
            
            logger.info(f"Sending transcription request to Whisper service")
            response_data = self._make_request(self.transcribe_url, data=data, files=files)
            
            # Validate response format
            if 'text' not in response_data:
                raise WhisperError("Invalid response format: missing 'text' field")
            
            # Extract and validate response
            result = {
                'text': response_data.get('text', '').strip(),
                'language': response_data.get('language', language or 'en'),
                'confidence': response_data.get('confidence', 0.8)  # Default confidence
            }
            
            # Validate detected language is supported
            if result['language'] not in self.SUPPORTED_LANGUAGES:
                logger.warning(f"Detected unsupported language: {result['language']}. Defaulting to English.")
                result['language'] = 'en'
            
            logger.info(f"Successfully transcribed audio. Detected language: {result['language']}")
            return result
            
        except WhisperError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in transcribe_audio_bytes: {e}")
            raise WhisperError(f"Transcription failed: {e}")
    
    def transcribe_base64_audio(self, base64_audio: str, language: str = None) -> Dict[str, Any]:
        """
        Transcribe base64-encoded audio to text.
        
        Args:
            base64_audio: Base64-encoded audio data
            language: Optional language hint
            
        Returns:
            Dict with transcription results
            
        Raises:
            WhisperError: If transcription fails
        """
        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(base64_audio)
            return self.transcribe_audio_bytes(audio_bytes, language)
            
        except Exception as e:
            logger.error(f"Failed to decode base64 audio: {e}")
            raise WhisperError(f"Invalid base64 audio data: {e}")
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text between supported languages.
        
        Args:
            text: Text to translate
            source_lang: Source language code (ISO 639-1)
            target_lang: Target language code (ISO 639-1)
            
        Returns:
            str: Translated text
            
        Raises:
            WhisperError: If translation fails or languages are unsupported
        """
        try:
            # Validate languages
            if source_lang not in self.SUPPORTED_LANGUAGES:
                raise WhisperError(f"Unsupported source language: {source_lang}")
            
            if target_lang not in self.SUPPORTED_LANGUAGES:
                raise WhisperError(f"Unsupported target language: {target_lang}")
            
            # Skip translation if same language
            if source_lang == target_lang:
                return text
            
            # Prepare translation request
            payload = {
                'text': text,
                'source_language': source_lang,
                'target_language': target_lang
            }
            
            logger.info(f"Translating text from {source_lang} to {target_lang}")
            response_data = self._make_request(self.translate_url, data=payload)
            
            # Extract translated text
            if 'translated_text' not in response_data:
                raise WhisperError("Invalid translation response format")
            
            translated_text = response_data['translated_text'].strip()
            logger.info("Successfully translated text")
            return translated_text
            
        except WhisperError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in translate_text: {e}")
            raise WhisperError(f"Translation failed: {e}")
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get list of supported languages.
        
        Returns:
            Dict mapping language codes to language names
        """
        return self.SUPPORTED_LANGUAGES.copy()
    
    def is_language_supported(self, language_code: str) -> bool:
        """
        Check if a language is supported.
        
        Args:
            language_code: ISO 639-1 language code
            
        Returns:
            bool: True if language is supported
        """
        return language_code in self.SUPPORTED_LANGUAGES
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if Whisper service is available and responsive.
        
        Returns:
            Dict with health status information
        """
        try:
            # Simple health check - try to get supported languages or ping endpoint
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            
            return {
                "status": "healthy",
                "base_url": self.base_url,
                "supported_languages": list(self.SUPPORTED_LANGUAGES.keys()),
                "service_responsive": True
            }
            
        except requests.exceptions.ConnectionError:
            return {
                "status": "unhealthy",
                "base_url": self.base_url,
                "error": "Connection refused - service may be down"
            }
        except requests.exceptions.Timeout:
            return {
                "status": "unhealthy", 
                "base_url": self.base_url,
                "error": "Service timeout"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "base_url": self.base_url, 
                "error": str(e)
            }


# Global client instance
whisper_client = WhisperClient()


def transcribe_audio_bytes(audio_bytes: bytes, language: str = None) -> Dict[str, Any]:
    """
    Convenience function for audio transcription.
    
    Args:
        audio_bytes: Raw audio data
        language: Optional language hint
        
    Returns:
        Dict with transcription results
        
    Raises:
        WhisperError: If transcription fails
    """
    return whisper_client.transcribe_audio_bytes(audio_bytes, language)


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Convenience function for text translation.
    
    Args:
        text: Text to translate
        source_lang: Source language code
        target_lang: Target language code
        
    Returns:
        str: Translated text
        
    Raises:
        WhisperError: If translation fails
    """
    return whisper_client.translate_text(text, source_lang, target_lang)