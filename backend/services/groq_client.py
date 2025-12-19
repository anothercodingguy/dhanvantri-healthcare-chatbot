"""
Groq client for high-performance LLM and Whisper integration.
Provides async methods for chat and audio transcription.
"""

import os
import logging
import base64
from typing import Optional, Dict, Any, List
from groq import AsyncGroq
from config import settings

logger = logging.getLogger(__name__)

class GroqServiceError(Exception):
    """Custom exception for Groq service errors."""
    pass

class GroqClient:
    """Client for interacting with Groq Cloud API."""
    
    def __init__(self):
        self.api_key = settings.groq_api_key
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found in settings. Service will fail if called.")
        
        self.client = AsyncGroq(api_key=self.api_key)
        self.model_name = settings.model_name
        self.stt_model = settings.stt_model

    async def chat(self, prompt: str, system_prompt: str = None, temperature: float = 0.5) -> str:
        """
        Send a chat message to Groq LLM and get response.
        
        Args:
            prompt: User's message/question
            system_prompt: System prompt for context
            temperature: Response randomness
            
        Returns:
            str: The model's response text
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            if self.model_name == "mock-model":
                logger.warning("Detected 'mock-model' in client. Forcing switch to llama-3.3-70b-versatile.")
                self.model_name = "llama-3.3-70b-versatile"

            logger.info(f"Sending chat request to Groq (Model: {self.model_name})")
            
            completion = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=settings.model_max_tokens,
                top_p=1,
                stream=False,
                stop=None,
            )
            
            response_text = completion.choices[0].message.content
            return response_text.strip()

        except Exception as e:
            logger.error(f"Groq Chat API error: {e}")
            raise GroqServiceError(f"Groq chat request failed: {e}")

    async def transcribe_audio(self, audio_content: bytes, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe audio content using Groq Whisper.
        
        Args:
            audio_content: Raw audio bytes
            language: Expected language code (optional hint)
            
        Returns:
            Dict with text and metadata
        """
        try:
            # Groq's transcription API requires a file-like object with a name
            # We wrap the bytes in a tuple (filename, file_content) or use io.BytesIO name wrapper
            # But the client.audio.transcriptions.create expects 'file' param.
            
            logger.info(f"Sending audio transcription request to Groq (Model: {self.stt_model})")
            
            # Optimizing for accuracy with temperature=0.0
            transcription = await self.client.audio.transcriptions.create(
                file=("audio.wav", audio_content),
                model=self.stt_model,
                language=language if language != "en" else None,
                response_format="json", 
                temperature=0.0
            )
            
            return {
                "text": transcription.text,
                "language": language
            }

        except Exception as e:
            logger.error(f"Groq STT API error: {e}")
            raise GroqServiceError(f"Groq STT request failed: {e}")
            
    async def transcribe_base64_audio(self, audio_base64: str, language: str = "en") -> Dict[str, Any]:
        """Helper to decode base64 and transcribe."""
        try:
            # Handle data URI prefix if present
            if "," in audio_base64:
                audio_base64 = audio_base64.split(",")[1]
                
            audio_bytes = base64.b64decode(audio_base64)
            return await self.transcribe_audio(audio_bytes, language)
        except Exception as e:
            raise GroqServiceError(f"Base64 decoding/transcription failed: {e}")


    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text using Groq LLM.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            str: Translated text
        """
        if source_lang == target_lang:
            return text
            
        try:
            prompt = f"Translate the following text from {source_lang} to {target_lang}. Return ONLY the translated text, no explanations or quotes.\n\nText: {text}"
            return await self.chat(prompt, temperature=0.1)
        except Exception as e:
            logger.error(f"Groq Translation error: {e}")
            raise GroqServiceError(f"Translation failed: {e}")


# Global client instance
groq_client = GroqClient()
