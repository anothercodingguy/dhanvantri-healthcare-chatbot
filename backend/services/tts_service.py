"""
Text-to-Speech service for multilingual audio generation using gTTS.
Supports English, Hindi, Kannada, Bengali, and Bhojpuri.
Runs in a separate thread to avoid blocking the asyncio event loop.
"""

import logging
import os
import base64
import tempfile
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict
from gtts import gTTS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSService:
    """Text-to-Speech service using gTTS for multilingual support."""
    
    def __init__(self):
        """Initializes the service."""
        try:
            logger.info("TTS Service initialized successfully.")
            self.executor = ThreadPoolExecutor(max_workers=3)
        except Exception as e:
            logger.error(f"Failed to initialize TTS Service: {e}")
            raise

        # Language code mapping for gTTS
        self.language_map = {
            'en': {'name': 'English', 'gtts_code': 'en'},
            'bn': {'name': 'Bengali', 'gtts_code': 'bn'}, 
            'bho': {'name': 'Bhojpuri', 'gtts_code': 'hi'},  # Use Hindi for Bhojpuri
            'hi': {'name': 'Hindi', 'gtts_code': 'hi'},
            'kn': {'name': 'Kannada', 'gtts_code': 'kn'},
            # Mapping frontend codes to simple codes if needed
            'en-US': {'name': 'English', 'gtts_code': 'en'},
            'bn-IN': {'name': 'Bengali', 'gtts_code': 'bn'}, 
            'bho-IN': {'name': 'Bhojpuri', 'gtts_code': 'hi'},
            'hi-IN': {'name': 'Hindi', 'gtts_code': 'hi'},
            'kn-IN': {'name': 'Kannada', 'gtts_code': 'kn'}
        }

    def _generate_speech_blocking(self, text: str, language_code: str) -> Optional[str]:
        """
        Blocking internal method to generate speech.
        """
        try:
            # Handle language code aliases
            lang_info = self.language_map.get(language_code)
            if not lang_info:
                # Try prefix match if full code not found
                prefix = language_code.split('-')[0]
                lang_info = self.language_map.get(prefix)
            
            if not lang_info:
                logger.error(f"Unsupported language code: {language_code}")
                return None

            if not text:
                logger.error("Text for speech synthesis is empty.")
                return None

            # Generate speech using gTTS
            gtts_code = lang_info['gtts_code']
            
            try:
                tts = gTTS(text=text, lang=gtts_code, slow=False)
                
                # Save to a temporary file
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                    tts.save(temp_file.name)
                    temp_file_path = temp_file.name

                # Read the audio file and encode as base64
                with open(temp_file_path, "rb") as audio_file:
                    audio_data = audio_file.read()
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')

                # Clean up temporary file
                os.unlink(temp_file_path)

                logger.info(f"Successfully generated TTS audio for language {language_code}, size: {len(audio_base64)} chars")
                return audio_base64

            except Exception as e:
                logger.error(f"gTTS generation failed: {e}")
                return None

        except Exception as e:
            logger.error(f"TTS generation failed for language {language_code}: {e}", exc_info=True)
            return None

    async def generate_speech_async(self, text: str, language_code: str = "en") -> Optional[str]:
        """
        Generates speech audio asynchronously using a thread pool.
        
        Args:
            text: The text to be spoken.
            language_code: The target language code.
            
        Returns:
            Optional[str]: Base64 encoded MP3 audio data.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self.executor, 
            self._generate_speech_blocking, 
            text, 
            language_code
        )

    async def generate_speech_direct_async(self, text: str, language_code: str = "en") -> Optional[str]:
        """Alias for generate_speech_async for consistency with previous API in chat.py"""
        return await self.generate_speech_async(text, language_code)

    def get_supported_languages(self) -> Dict[str, str]:
        """Returns a dictionary of supported language codes and their names."""
        # Return unique simple codes
        return {k: v['name'] for k, v in self.language_map.items() if '-' not in k}

# Global TTS service instance
try:
    tts_service = TTSService()
except Exception as e:
    logger.critical(f"Could not initialize TTSService: {e}")
    tts_service = None