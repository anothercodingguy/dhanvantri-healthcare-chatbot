"""
Text-to-Speech service using Microsoft Edge's Neural TTS (via edge-tts).
Provides high-quality, human-like voice synthesis for free.
"""

import logging
import base64
import os
import tempfile
import asyncio
from typing import Optional, Dict
import edge_tts

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EdgeTTSService:
    """
    TTS Service using edge-tts for high-quality neural voices.
    """
    
    def __init__(self):
        """Initializes the Edge TTS service with language mappings."""
        try:
            logger.info("Initializing Edge TTS Service (Neural Voices)...")
            
            # Mapping of language codes to specific Neural voices
            # Selected for natural sounding medical context
            self.voice_map = {
                'en': 'en-US-ChristopherNeural', # Male voice
                'hi': 'hi-IN-MadhurNeural',      # Male Hindi voice
                'bn': 'bn-IN-TanishaaNeural',    # Bengali (Keep Female)
                'kn': 'kn-IN-GaganNeural',       # Kannada (Male)
                'ta': 'ta-IN-ValluvarNeural',    # Tamil (Male)
                'te': 'te-IN-MohanNeural',       # Telugu (Male)
                'mr': 'mr-IN-AarohiNeural',      # Marathi (Female)
                'gu': 'gu-IN-DhwaniNeural',      # Gujarati (Female)
                'ur': 'ur-IN-SalmanNeural',      # Urdu (Male)
                'bho': 'hi-IN-MadhurNeural',     # Fallback
            }
            
            # Map complex codes (e.g., en-US) to simple codes
            self.complex_map = {
                'en-US': 'en',
                'en-GB': 'en',
                'en-IN': 'en',
                'hi-IN': 'hi',
                'bn-IN': 'bn',
                'kn-IN': 'kn',
                'bho-IN': 'bho'
            }
            
            # Voice speed/pitch adjustments if needed (default "0%")
            self.rate = "+0%"
            self.volume = "+0%"
            self.pitch = "+0Hz"
            
        except Exception as e:
            logger.critical(f"Failed to initialize Edge TTS Service: {e}")
            raise

    def get_voice(self, language_code: str) -> str:
        """Determines the best voice for the given language."""
        # Clean language code
        lang = language_code.split('-')[0].lower()
        
        # Check specific full code match first
        if language_code in self.complex_map:
            lang = self.complex_map[language_code]
            
        return self.voice_map.get(lang, self.voice_map['en'])

    async def generate_speech_async(self, text: str, language_code: str = "en") -> Optional[str]:
        """
        Generates speech using Edge TTS.
        
        Args:
            text: Text to synthesize
            language_code: Target language
            
        Returns:
            str: Base64 encoded MP3 audio
        """
        if not text:
            logger.warning("Empty text provided for TTS")
            return None
            
        try:
            voice = self.get_voice(language_code)
            logger.info(f"Generating TTS for lang='{language_code}' using voice='{voice}'")
            
            # Create communicate object
            communicate = edge_tts.Communicate(text, voice, rate=self.rate, volume=self.volume, pitch=self.pitch)
            
            # Stream to memory (or temp file if needed, but we can capture bytes directly)
            # edge-tts save() is awaitable
            
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_path = temp_file.name
                
            await communicate.save(temp_path)
            
            # Read back and encode
            if os.path.exists(temp_path):
                with open(temp_path, "rb") as audio_file:
                    audio_data = audio_file.read()
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                # Cleanup
                os.unlink(temp_path)
                return audio_base64
            else:
                logger.error("TTS file was not created successfully")
                return None
                
        except Exception as e:
            logger.error(f"Edge TTS generation failed: {e}", exc_info=True)
            return None

    def get_supported_languages(self) -> Dict[str, str]:
        """Returns supported languages."""
        return {
            'en': 'English (Neural)',
            'hi': 'Hindi (Neural)',
            'bn': 'Bengali (Neural)',
            'kn': 'Kannada (Neural)',
            'bho': 'Bhojpuri (Hindi-Variant Neural)'
        }

# Global instance
try:
    edge_tts_service = EdgeTTSService()
except Exception as e:
    logger.error(f"Could not initialize global EdgeTTSService: {e}")
    edge_tts_service = None
