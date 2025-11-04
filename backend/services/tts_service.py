"""Text-to-Speech service for multilingual audio generation using gTTS.
Supports English, Hindi, Kannada, Bengali, and Bhojpuri."""

import logging
import os
import base64
import tempfile
from typing import Optional, Dict
from gtts import gTTS
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSService:
    """Text-to-Speech service using gTTS for multilingual support."""
    
    def __init__(self):
        """Initializes the service."""
        try:
            logger.info("TTS Service initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize TTS Service: {e}")
            raise

        # Language code mapping for gTTS
        self.language_map = {
            'en-US': {'name': 'English', 'gtts_code': 'en'},
            'bn-IN': {'name': 'Bengali', 'gtts_code': 'bn'}, 
            'bho-IN': {'name': 'Bhojpuri', 'gtts_code': 'hi'},  # Use Hindi for Bhojpuri
            'hi-IN': {'name': 'Hindi', 'gtts_code': 'hi'},
            'kn-IN': {'name': 'Kannada', 'gtts_code': 'kn'}
        }

    def translate_text(self, text: str, language_code: str) -> str:
        """Returns the text as-is since translation is handled by the frontend."""
        # For the free deployment, we assume text is already in the correct language
        # Translation can be handled by the frontend or external services
        return text

    def generate_speech(self, text_to_speak: str, language_code: str = "en-US") -> Optional[str]:
        """Generates speech audio from text in the specified language.
        
        Args:
            text_to_speak (str): The text to be spoken.
            language_code (str): The target language code (e.g., 'hi-IN').
            
        Returns:
            Optional[str]: Base64 encoded MP3 audio data, or None if generation fails.
        """
        try:
            lang_info = self.language_map.get(language_code)
            if not lang_info:
                logger.error(f"Unsupported language code: {language_code}")
                return None

            # Use the text as-is (translation handled by frontend)
            translated_text = text_to_speak
            if not translated_text:
                logger.error("Text for speech synthesis is empty.")
                return None

            logger.info(f"Generating TTS for language {language_code}.")
            logger.info(f"Text to synthesize: {translated_text[:100]}...")

            # Step 2: Generate speech using gTTS
            gtts_code = lang_info['gtts_code']
            
            try:
                tts = gTTS(text=translated_text, lang=gtts_code, slow=False)
                
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

    def get_supported_languages(self) -> Dict[str, str]:
        """Returns a dictionary of supported language codes and their names."""
        return {code: info['name'] for code, info in self.language_map.items()}

# Global TTS service instance
# This creates a single instance of the service that can be imported and used across your application.
try:
    tts_service = TTSService()
except Exception as e:
    logger.critical(f"Could not initialize TTSService: {e}")
    tts_service = None
# Example usage:
if __name__ == '__main__':
    if tts_service:
        print("TTS Service Initialized. Running examples...")
        
        # --- Example 1: Generate speech in Hindi ---
        english_text = "Hello, how are you doing today? I hope you are having a wonderful day."
        hindi_language_code = "hi-IN"
        print(f"\nGenerating speech for: '{english_text}' in Hindi ({hindi_language_code})")
        audio_content_base64 = tts_service.generate_speech(english_text, hindi_language_code)
        
        if audio_content_base64:
            # Save the audio to a file to verify (MP3 format)
            output_filename = "output_hindi.mp3"
            with open(output_filename, "wb") as audio_file:
                audio_file.write(base64.b64decode(audio_content_base64))
            print(f"Audio content saved to '{output_filename}'.")
        else:
            print("Failed to generate Hindi audio.")

        # --- Example 2: Generate speech in English ---
        print(f"\nGenerating speech for: '{english_text}' in English (en-US)")
        audio_content_base64_eng = tts_service.generate_speech(english_text, "en-US")
        
        if audio_content_base64_eng:
            output_filename_eng = "output_english.mp3"
            with open(output_filename_eng, "wb") as audio_file:
                audio_file.write(base64.b64decode(audio_content_base64_eng))
            print(f"Audio content saved to '{output_filename_eng}'.")
        else:
            print("Failed to generate English audio.")

        # --- Example 3: Get supported languages ---
        print("\nSupported Languages:")
        print(tts_service.get_supported_languages())
    else:
        print("TTS Service failed to initialize.")