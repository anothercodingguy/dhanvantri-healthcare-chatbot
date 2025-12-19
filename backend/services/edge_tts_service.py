"""
Robust TTS Service.
Primary: Microsoft Edge Neural TTS (In-Memory Streaming)
Fallback: Google TTS (gTTS)
"""

import logging
import base64
import asyncio
import io
from typing import Optional, Dict
import edge_tts
from gtts import gTTS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobustTTSService:
    """
    TTS Service with Primary (Edge) and Secondary (Google) engines.
    Uses in-memory stream processing to avoid file I/O permissions issues.
    """
    
    def __init__(self):
        """Initializes the service with language mappings."""
        try:
            logger.info("Initializing Robust TTS Service...")
            
            # --- Primary: Edge TTS Config ---
            self.voice_map = {
                'en': 'en-US-ChristopherNeural', # Male voice
                'hi': 'hi-IN-MadhurNeural',      # Male Hindi voice
                'bn': 'bn-IN-TanishaaNeural',    # Bengali
                'kn': 'kn-IN-GaganNeural',       # Kannada
                'ta': 'ta-IN-ValluvarNeural',    # Tamil
                'te': 'te-IN-MohanNeural',       # Telugu
                'mr': 'mr-IN-AarohiNeural',      # Marathi
                'gu': 'gu-IN-DhwaniNeural',      # Gujarati
                'ur': 'ur-IN-SalmanNeural',      # Urdu
                'bho': 'hi-IN-MadhurNeural',     # Fallback
            }
            
            self.complex_map = {
                'en-US': 'en', 'en-GB': 'en', 'en-IN': 'en',
                'hi-IN': 'hi', 'bn-IN': 'bn', 'kn-IN': 'kn', 'bho-IN': 'bho'
            }
            
            self.rate = "+0%"
            
        except Exception as e:
            logger.critical(f"Failed to initialize TTS Service: {e}")
            raise

    def get_voice(self, language_code: str) -> str:
        """Determines the best Edge voice for the given language."""
        lang = language_code.split('-')[0].lower()
        if language_code in self.complex_map:
            lang = self.complex_map[language_code]
        return self.voice_map.get(lang, self.voice_map['en'])

    async def generate_speech_async(self, text: str, language_code: str = "en") -> Optional[str]:
        """
        Generates speech using Strategy Pattern (Primary -> Fallback).
        Returns Base64 MP3.
        """
        if not text:
            return None
            
        # Attempt Primary (Edge TTS)
        try:
            logger.info(f"Attempting Primary TTS (Edge) for {language_code}...")
            return await self._generate_edge_tts(text, language_code)
        except Exception as e:
            logger.error(f"Primary TTS Failed: {e}. Switching to Fallback.")
            
            # Attempt Secondary (gTTS)
            try:
                logger.info(f"Attempting Secondary TTS (Google) for {language_code}...")
                return await self._generate_gtts(text, language_code)
            except Exception as e2:
                logger.critical(f"All TTS strategies failed: {e2}")
                return None

    # --- Strategy 1: Edge TTS (In-Memory) ---
    async def _generate_edge_tts(self, text: str, language_code: str) -> str:
        voice = self.get_voice(language_code)
        communicate = edge_tts.Communicate(text, voice, rate=self.rate)
        
        # Stream chunks into memory
        audio_stream = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])
                
        audio_bytes = audio_stream.getvalue()
        
        if len(audio_bytes) == 0:
            raise Exception("Edge TTS returned 0 bytes")
            
        return base64.b64encode(audio_bytes).decode('utf-8')

    # --- Strategy 2: gTTS (Blocking wrapped in Async) ---
    async def _generate_gtts(self, text: str, language_code: str) -> str:
        def _gtts_task():
            # Clean lang code for gTTS (it expects 'en', 'hi', not 'en-US' usually)
            simple_lang = language_code.split('-')[0].lower()
            
            # gTTS writes to file-like object
            fp = io.BytesIO()
            tts = gTTS(text=text, lang=simple_lang, slow=False)
            tts.write_to_fp(fp)
            return fp.getvalue()

        # Run blocking gTTS in thread pool
        audio_bytes = await asyncio.get_running_loop().run_in_executor(None, _gtts_task)
        
        if len(audio_bytes) == 0:
            raise Exception("gTTS returned 0 bytes")
            
        return base64.b64encode(audio_bytes).decode('utf-8')

    def get_supported_languages(self) -> Dict[str, str]:
        return {
            'en': 'English',
            'hi': 'Hindi',
            'bn': 'Bengali',
            'kn': 'Kannada'
        }

# Global instance
try:
    # Rename to maintain compatibility with existing imports
    edge_tts_service = RobustTTSService() 
except Exception as e:
    logger.error(f"Could not initialize global TTSService: {e}")
    edge_tts_service = None
