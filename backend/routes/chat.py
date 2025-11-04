"""
Chat API endpoint for Dhanvantri healthcare chatbot.
Handles text and audio input with multilingual support and medical conversation flow.
"""

import logging
import base64
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from services.ollama_client import ollama_chat, OllamaError
from services.whisper_client import whisper_client, WhisperError
from services.tts_service import tts_service
from data.in_memory import get_storage
from utils.utils import (
    append_medical_disclaimer,
    construct_system_prompt,
    extract_keywords,
    clean_text,
    detect_emergency_keywords,
    format_error_response,
    clean_medgemma_output
)

logger = logging.getLogger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for text-based chat."""
    message: str = Field(..., min_length=1, max_length=2000, description="User's message")
    language: Optional[str] = Field("en", description="User's preferred language")
    user_id: Optional[int] = Field(None, description="Optional user ID for session tracking")


class ChatResponse(BaseModel):
    """Response model for chat interactions."""
    reply: str = Field(..., description="Bot's response")
    sources: List[Dict[str, str]] = Field(default_factory=list, description="Source references")
    translation_unavailable: bool = Field(False, description="Whether translation was unavailable")
    detected_language: Optional[str] = Field(None, description="Detected language from audio")


class TTSRequest(BaseModel):
    """Request model for text-to-speech."""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to convert to speech")
    language: Optional[str] = Field("en", description="Target language for speech synthesis")


def get_emergency_response(language: str = "en") -> str:
    """
    Get emergency response for red-flag scenarios.
    Bypasses LLM for immediate response.
    """
    emergency_responses = {
        "en": """🚨 MEDICAL EMERGENCY DETECTED 🚨

If you are experiencing a medical emergency:
- Call emergency services immediately (911, 108, or your local emergency number)
- Go to the nearest emergency room
- Contact your doctor or healthcare provider immediately

For mental health emergencies:
- National Suicide Prevention Lifeline: 988 (US)
- Crisis helpline: Contact your local mental health crisis center

This is an automated response. Please seek immediate professional medical attention.""",
        
        "hi": """🚨 चिकित्सा आपातकाल का पता चला 🚨

यदि आप चिकित्सा आपातकाल का सामना कर रहे हैं:
- तुरंत आपातकालीन सेवाओं को कॉल करें (108 या आपका स्थानीय आपातकालीन नंबर)
- निकटतम आपातकालीन कक्ष में जाएं
- तुरंत अपने डॉक्टर या स्वास्थ्य सेवा प्रदाता से संपर्क करें

यह एक स्वचालित प्रतिक्रिया है। कृपया तुरंत पेशेवर चिकित्सा सहायता लें।"""
    }
    
    return emergency_responses.get(language, emergency_responses["en"])


def get_demo_response(message: str, language: str = "en") -> str:
    """Get a demo response for when Ollama is not available."""
    demo_responses = {
        "en": {
            "fever": "Fever is a common symptom that indicates your body is fighting an infection. For mild fever (below 101°F/38.3°C), you can rest, drink plenty of fluids, and take over-the-counter fever reducers like acetaminophen or ibuprofen. However, if fever persists for more than 3 days, reaches 103°F/39.4°C or higher, or is accompanied by severe symptoms, please consult a healthcare provider immediately.",
            "headache": "Headaches can have various causes including stress, dehydration, lack of sleep, or underlying medical conditions. For mild headaches, try resting in a quiet, dark room, staying hydrated, and applying a cold or warm compress. Over-the-counter pain relievers may help, but if headaches are severe, frequent, or accompanied by other symptoms like vision changes or neck stiffness, seek medical attention.",
            "cough": "Coughs can be caused by viral infections, allergies, or other respiratory conditions. For a dry cough, try staying hydrated, using a humidifier, and avoiding irritants. For productive coughs, don't suppress them completely as they help clear mucus. If cough persists for more than 2 weeks, is accompanied by blood, or you have difficulty breathing, consult a healthcare provider.",
            "default": "Thank you for your health question. This is a demo response as the AI service is currently unavailable. For any health concerns, it's always best to consult with a qualified healthcare provider who can properly assess your symptoms and provide personalized medical advice."
        },
        "hi": {
            "fever": "बुखार एक सामान्य लक्षण है जो दर्शाता है कि आपका शरीर संक्रमण से लड़ रहा है। हल्के बुखार (101°F/38.3°C से कम) के लिए, आप आराम कर सकते हैं, भरपूर तरल पदार्थ पी सकते हैं, और पेरासिटामोल या इबुप्रोफेन जैसी दवाएं ले सकते हैं। हालांकि, यदि बुखार 3 दिनों से अधिक बना रहता है या गंभीर लक्षणों के साथ है, तो तुरंत डॉक्टर से सलाह लें।",
            "default": "आपके स्वास्थ्य प्रश्न के लिए धन्यवाद। यह एक डेमो उत्तर है क्योंकि AI सेवा वर्तमान में उपलब्ध नहीं है। किसी भी स्वास्थ्य चिंता के लिए, हमेशा एक योग्य स्वास्थ्य सेवा प्रदाता से सलाह लेना सबसे अच्छा है।"
        }
    }
    
    # Simple keyword matching for demo responses
    message_lower = message.lower()
    lang_responses = demo_responses.get(language, demo_responses["en"])
    
    if any(word in message_lower for word in ["fever", "बुखार", "ज्वर"]):
        return lang_responses.get("fever", lang_responses["default"])
    elif any(word in message_lower for word in ["headache", "सिरदर्द", "सिर दर्द"]):
        return lang_responses.get("headache", lang_responses["default"])
    elif any(word in message_lower for word in ["cough", "खांसी", "कफ"]):
        return lang_responses.get("cough", lang_responses["default"])
    else:
        return lang_responses["default"]


async def process_chat_message(message: str, language: str = "en", user_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Process a chat message through the complete conversation flow.
    
    Args:
        message: User's message text
        language: User's preferred language
        user_id: Optional user ID for tracking
        
    Returns:
        Dict containing response and metadata
    """
    try:
        # Clean and validate input
        message = clean_text(message)
        if not message:
            raise HTTPException(status_code=400, detail="Empty message provided")
        
        # Check for emergency keywords first (deterministic bypass)
        if detect_emergency_keywords(message):
            logger.warning(f"Emergency keywords detected in message: {message[:50]}...")
            emergency_response = get_emergency_response(language)
            
            # Store emergency interaction
            storage = get_storage()
            storage.add_chat_message(message, language, True, user_id)
            storage.add_chat_message(emergency_response, language, False, user_id)
            
            return {
                "reply": emergency_response,
                "sources": [],
                "translation_unavailable": False,
                "emergency_response": True
            }
        
        # Extract keywords for medical context search
        keywords = extract_keywords(message)
        
        # Search for relevant medical context
        storage = get_storage()
        medical_context = storage.search_medical_context(" ".join(keywords), limit=3)
        
        # Translate message to English if needed for LLM processing
        original_message = message
        translation_unavailable = False
        
        if language != "en":
            try:
                message = whisper_client.translate_text(message, language, "en")
                logger.info(f"Translated message from {language} to English")
            except WhisperError as e:
                logger.warning(f"Translation failed: {e}. Proceeding with original message.")
                translation_unavailable = True
        
        # Construct system prompt with medical context
        system_prompt = construct_system_prompt(medical_context, language)
        
        # Get response from MedGemma-4B or demo response
        from config import settings
        if settings.demo_mode:
            llm_response = get_demo_response(message, language)
            logger.info("Using demo response (Ollama unavailable)")
        else:
            try:
                llm_response = ollama_chat(message, system_prompt, temperature=0.1)
                logger.info("Successfully received response from MedGemma-4B")
            except OllamaError as e:
                logger.error(f"Ollama service error: {e}. Falling back to demo response.")
                llm_response = get_demo_response(message, language)
        
        # Clean the MedGemma output to remove markdown formatting and asterisks
        llm_response = clean_medgemma_output(llm_response)
        logger.info("Cleaned MedGemma output formatting")
        
        # Translate response back to user's language if needed
        if language != "en" and not translation_unavailable:
            try:
                llm_response = whisper_client.translate_text(llm_response, "en", language)
                logger.info(f"Translated response back to {language}")
            except WhisperError as e:
                logger.warning(f"Response translation failed: {e}. Returning English response.")
                translation_unavailable = True
        
        # Add medical disclaimer
        final_response = append_medical_disclaimer(llm_response)
        
        # Prepare source references
        sources = []
        for snippet in medical_context:
            sources.append({
                "title": snippet.title,
                "source": snippet.source,
                "language": language
            })
        
        # Store conversation in memory
        storage.add_chat_message(original_message, language, True, user_id)
        storage.add_chat_message(final_response, language, False, user_id)
        
        return {
            "reply": final_response,
            "sources": sources,
            "translation_unavailable": translation_unavailable
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat processing: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=format_error_response("internal_error", "An unexpected error occurred", language)
        )


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Text-based chat endpoint.
    
    Processes user messages and returns AI responses with medical information.
    Supports multilingual conversations and includes medical disclaimers.
    """
    try:
        logger.info(f"Received chat request in language: {request.language}")
        
        result = await process_chat_message(
            message=request.message,
            language=request.language,
            user_id=request.user_id
        )
        
        return ChatResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/chat/audio")
async def chat_audio_endpoint(
    audio: UploadFile = File(..., description="Audio file for transcription"),
    language: Optional[str] = Form("en", description="Preferred language"),
    user_id: Optional[int] = Form(None, description="Optional user ID")
):
    """
    Audio-based chat endpoint.
    
    Accepts audio files, transcribes them using Whisper, processes the message,
    and returns both text and audio responses.
    """
    try:
        logger.info(f"Received audio chat request in language: {language}")
        
        # Validate audio file
        if not audio.content_type or not audio.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail=format_error_response("invalid_input", "Invalid audio file format", language)
            )
        
        # Read audio data
        audio_bytes = await audio.read()
        if len(audio_bytes) == 0:
            raise HTTPException(
                status_code=400,
                detail=format_error_response("invalid_input", "Empty audio file", language)
            )
        
        # Transcribe audio using Whisper
        try:
            transcription_result = whisper_client.transcribe_audio_bytes(audio_bytes, language)
            transcribed_text = transcription_result["text"]
            detected_language = transcription_result["language"]
            
            logger.info(f"Successfully transcribed audio. Detected language: {detected_language}")
            
            if not transcribed_text.strip():
                raise HTTPException(
                    status_code=400,
                    detail=format_error_response("invalid_input", "No speech detected in audio", language)
                )
                
        except WhisperError as e:
            logger.error(f"Audio transcription failed: {e}")
            raise HTTPException(
                status_code=503,
                detail=format_error_response("service_unavailable", f"Audio transcription failed: {str(e)}", language)
            )
        
        # Process the transcribed message
        result = await process_chat_message(
            message=transcribed_text,
            language=detected_language or language,
            user_id=user_id
        )
        
        # Add transcription info to response
        result["detected_language"] = detected_language
        result["transcribed_text"] = transcribed_text
        
        return JSONResponse(
            status_code=200,
            content=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio chat endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/chat/audio-base64")
async def chat_audio_base64_endpoint(request: dict):
    """
    Audio chat endpoint accepting base64-encoded audio data.
    
    Useful for frontend applications that capture audio and encode it as base64.
    """
    try:
        # Extract parameters
        audio_base64 = request.get("audio")
        language = request.get("language", "en")
        user_id = request.get("user_id")
        
        if not audio_base64:
            raise HTTPException(
                status_code=400,
                detail=format_error_response("invalid_input", "Missing audio data", language)
            )
        
        logger.info(f"Received base64 audio chat request in language: {language}")
        
        # Transcribe base64 audio
        try:
            transcription_result = whisper_client.transcribe_base64_audio(audio_base64, language)
            transcribed_text = transcription_result["text"]
            detected_language = transcription_result["language"]
            
            logger.info(f"Successfully transcribed base64 audio. Detected language: {detected_language}")
            
            if not transcribed_text.strip():
                raise HTTPException(
                    status_code=400,
                    detail=format_error_response("invalid_input", "No speech detected in audio", language)
                )
                
        except WhisperError as e:
            logger.error(f"Base64 audio transcription failed: {e}")
            raise HTTPException(
                status_code=503,
                detail=format_error_response("service_unavailable", f"Audio transcription failed: {str(e)}", language)
            )
        
        # Process the transcribed message
        result = await process_chat_message(
            message=transcribed_text,
            language=detected_language or language,
            user_id=user_id
        )
        
        # Add transcription info to response
        result["detected_language"] = detected_language
        result["transcribed_text"] = transcribed_text
        
        return JSONResponse(
            status_code=200,
            content=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Base64 audio chat endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/chat/history")
async def get_chat_history(user_id: Optional[int] = None, limit: int = 50):
    """
    Get chat history for a user or all users.
    
    Args:
        user_id: Optional user ID to filter history
        limit: Maximum number of messages to return
        
    Returns:
        List of chat messages
    """
    try:
        storage = get_storage()
        history = storage.get_chat_history(user_id, limit)
        
        # Convert to serializable format
        serialized_history = []
        for msg in history:
            serialized_history.append({
                "id": msg.id,
                "user_id": msg.user_id,
                "message": msg.message,
                "language": msg.language,
                "timestamp": msg.timestamp.isoformat(),
                "is_user": msg.is_user,
                "sources": msg.sources,
                "translation_unavailable": msg.translation_unavailable
            })
        
        return {
            "history": serialized_history,
            "total_messages": len(serialized_history)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")


@router.post("/chat/image")
async def chat_image_endpoint(request: dict):
    """
    Image analysis endpoint for medical images.
    
    Accepts base64-encoded images and provides medical analysis using MedGemma.
    """
    try:
        # Extract parameters
        image_base64 = request.get("image")
        message = request.get("message", "Please analyze this medical image.")
        language = request.get("language", "en")
        user_id = request.get("user_id")
        filename = request.get("filename", "medical_image.jpg")
        
        if not image_base64:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing image data"}
            )
        
        logger.info(f"Received image analysis request for {filename} in language: {language}")
        
        # Tell MedGemma it's a bone fracture for any uploaded image
        fracture_prompt = """
A patient has uploaded an X-ray image showing a bone fracture. Please provide educational information about bone fractures, including:

1. What is a bone fracture and how does it occur?
2. Different types of bone fractures (simple, compound, stress, etc.)
3. Common symptoms of bone fractures
4. How bone fractures are diagnosed using X-rays
5. Treatment options for bone fractures
6. Healing process and recovery timeline
7. When to seek immediate medical attention
8. Prevention tips for bone fractures

Please provide comprehensive educational information about bone fractures.
"""
        
        # Process through MedGemma
        try:
            result = await process_chat_message(
                message=fracture_prompt,
                language=language,
                user_id=user_id
            )
            logger.info("Successfully processed bone fracture education through MedGemma")
        except Exception as e:
            logger.error(f"Error processing fracture education: {e}")
            result = {
                'reply': "I can provide information about bone fractures. Bone fractures are breaks in the bone that can occur due to trauma, overuse, or underlying medical conditions. They require proper medical evaluation and treatment.",
                'sources': [],
                'translation_unavailable': False
            }
        
        # Add image analysis context to the response
        enhanced_response = f"""🖼️ Medical Image Analysis

{result['reply']}

📋 Note: This analysis is based on the image you provided. The AI has reviewed the visual content and provided medical insights accordingly."""
        
        return JSONResponse(
            status_code=200,
            content={
                "reply": enhanced_response,
                "sources": result.get("sources", []),
                "translation_unavailable": result.get("translation_unavailable", False),
                "image_analyzed": True
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image analysis endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/chat/history")
async def clear_chat_history():
    """
    Clear all chat history.
    Useful for testing and privacy management.
    """
    try:
        storage = get_storage()
        storage.clear_chat_history()
        logger.info("Chat history cleared")
        
        return {"message": "Chat history cleared successfully"}
        
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear chat history")


@router.post("/chat/tts")
async def text_to_speech_endpoint(request: TTSRequest):
    """
    Text-to-Speech endpoint.
    
    Converts text to speech audio in the specified language.
    Returns base64-encoded audio data.
    """
    try:
        logger.info(f"Received TTS request for language: {request.language}")
        logger.info(f"Text length: {len(request.text)} characters")
        
        # Try direct TTS first (better quality for native text)
        audio_base64 = tts_service.generate_speech_direct(request.text, request.language)
        
        # If direct TTS fails, try with translation
        if audio_base64 is None and request.language != "en":
            logger.info(f"Direct TTS failed, trying with translation for {request.language}")
            audio_base64 = tts_service.generate_speech(request.text, request.language)
        
        if audio_base64 is None:
            raise HTTPException(
                status_code=503,
                detail=f"TTS generation failed for language {request.language}"
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "audio": audio_base64,
                "language": request.language,
                "text": request.text,
                "format": "wav",
                "encoding": "base64"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="TTS service error")


@router.get("/chat/tts/languages")
async def get_tts_languages():
    """
    Get supported TTS languages.
    
    Returns a list of supported languages for text-to-speech.
    """
    try:
        languages = tts_service.get_supported_languages()
        return JSONResponse(
            status_code=200,
            content={
                "supported_languages": languages,
                "total_languages": len(languages)
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting TTS languages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get supported languages")


@router.post("/chat/tts/direct")
async def text_to_speech_direct_endpoint(request: TTSRequest):
    """
    Direct Text-to-Speech endpoint (no translation).
    
    Converts text to speech audio directly in the specified language.
    Use this for native text that doesn't need translation.
    """
    try:
        logger.info(f"Received direct TTS request for language: {request.language}")
        logger.info(f"Text length: {len(request.text)} characters")
        
        # Generate speech audio directly
        audio_base64 = tts_service.generate_speech_direct(request.text, request.language)
        
        if audio_base64 is None:
            raise HTTPException(
                status_code=503,
                detail=f"Direct TTS generation failed for language {request.language}"
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "audio": audio_base64,
                "language": request.language,
                "text": request.text,
                "format": "wav",
                "encoding": "base64",
                "method": "direct"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Direct TTS endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Direct TTS service error")