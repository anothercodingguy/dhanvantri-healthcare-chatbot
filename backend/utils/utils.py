"""
Utility functions for Dhanvantri chatbot.
Includes medical disclaimer, system prompt construction, and text processing helpers.
"""

import re
from typing import List, Optional
from data.in_memory import DiseaseSnippet


# Medical disclaimer removed as requested


def append_medical_disclaimer(response: str) -> str:
    """
    Return response without medical disclaimer.
    
    Args:
        response: The original response text
        
    Returns:
        Response without disclaimer
    """
    return response


def construct_system_prompt(medical_context: List[DiseaseSnippet] = None, language: str = "en") -> str:
    """
    Construct system prompt for medical conversations with MedGemma-4B.
    
    Args:
        medical_context: List of relevant medical facts to include as context
        language: Target language for the response
        
    Returns:
        Formatted system prompt for the LLM
    """
    base_prompt = """You are Dhanvantri, a helpful medical education assistant. You provide accurate, evidence-based health information to help users understand medical topics.

Guidelines:
- Provide clear, accurate medical information based on established medical knowledge
- Always emphasize that your information is educational and not a substitute for professional medical advice
- If asked about serious symptoms or emergencies, strongly recommend immediate medical attention
- Be empathetic and supportive while maintaining medical accuracy
- Keep responses concise but informative
- If uncertain about any medical information, recommend consulting healthcare professionals"""

    # Add language instruction if not English
    if language != "en":
        language_names = {
            "hi": "Hindi",
            "bn": "Bengali", 
            "bho": "Bhojpuri",
            "kn": "Kannada"
        }
        lang_name = language_names.get(language, language)
        base_prompt += f"\n- Respond in {lang_name} language"

    # Add medical context if provided
    if medical_context:
        context_text = "\n\nRelevant Medical Information:\n"
        for i, snippet in enumerate(medical_context[:3], 1):  # Limit to 3 most relevant
            content = snippet.get_content(language)
            context_text += f"{i}. {snippet.title}: {content[:200]}...\n"
        base_prompt += context_text

    return base_prompt


def extract_keywords(text: str) -> List[str]:
    """
    Extract potential medical keywords from text for context search.
    
    Args:
        text: Input text to extract keywords from
        
    Returns:
        List of extracted keywords
    """
    if not text:
        return []
    
    # Convert to lowercase and remove punctuation
    cleaned_text = re.sub(r'[^\w\s]', ' ', text.lower())
    
    # Split into words and filter out common stop words
    stop_words = {
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
        'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
        'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
        'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
        'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
        'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after',
        'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
        'further', 'then', 'once', 'can', 'could', 'should', 'would', 'will', 'shall'
    }
    
    words = cleaned_text.split()
    keywords = [word for word in words if len(word) > 2 and word not in stop_words]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword not in seen:
            seen.add(keyword)
            unique_keywords.append(keyword)
    
    return unique_keywords[:10]  # Limit to 10 most relevant keywords


def clean_text(text: str) -> str:
    """
    Clean and normalize text for processing.
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace and normalize line endings
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove any control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    return text


def detect_emergency_keywords(text: str) -> bool:
    """
    Detect emergency keywords that should trigger immediate response.
    This is a simple deterministic check for red-flag scenarios.
    
    Args:
        text: Input text to check for emergency keywords
        
    Returns:
        True if emergency keywords detected, False otherwise
    """
    if not text:
        return False
    
    text_lower = text.lower()
    
    # Emergency keywords in multiple languages
    emergency_keywords = [
        # English
        'emergency', 'urgent', 'help', 'dying', 'suicide', 'kill myself', 'chest pain',
        'heart attack', 'stroke', 'bleeding', 'unconscious', 'overdose', 'poison',
        'severe pain', 'can\'t breathe', 'difficulty breathing', 'choking',
        
        # Hindi (transliterated)
        'emergency', 'madad', 'bachao', 'dard', 'saans nahi aa rahi',
        
        # Common medical emergencies
        'accident', 'injury', 'broken bone', 'severe headache', 'high fever',
        'vomiting blood', 'blood in stool', 'severe abdominal pain'
    ]
    
    return any(keyword in text_lower for keyword in emergency_keywords)


def format_error_response(error_type: str, message: str, language: str = "en") -> dict:
    """
    Format standardized error responses.
    
    Args:
        error_type: Type of error (e.g., 'translation_unavailable', 'service_unavailable')
        message: Error message
        language: Language for the response
        
    Returns:
        Formatted error response dictionary
    """
    # Translate common error messages
    error_messages = {
        "en": {
            "translation_unavailable": "Translation service is currently unavailable. Response provided in English.",
            "service_unavailable": "Service is temporarily unavailable. Please try again later.",
            "invalid_input": "Invalid input provided. Please check your request and try again."
        },
        "hi": {
            "translation_unavailable": "अनुवाद सेवा अभी उपलब्ध नहीं है। उत्तर अंग्रेजी में दिया गया है।",
            "service_unavailable": "सेवा अस्थायी रूप से अनुपलब्ध है। कृपया बाद में पुनः प्रयास करें।",
            "invalid_input": "अमान्य इनपुट प्रदान किया गया। कृपया अपना अनुरोध जांचें और पुनः प्रयास करें।"
        }
    }
    
    # Get localized message if available, otherwise use provided message
    localized_messages = error_messages.get(language, error_messages["en"])
    localized_message = localized_messages.get(error_type, message)
    
    return {
        "error": error_type,
        "message": localized_message,
        "translation_unavailable": language != "en"
    }


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to specified length while preserving word boundaries.
    
    Args:
        text: Text to truncate
        max_length: Maximum length of text
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    # Find the last space before max_length
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + "..."



def clean_medgemma_output(text: str) -> str:
    """
    Clean MedGemma output by removing markdown formatting, asterisks, and other unwanted characters.
    Makes the output more readable and professional.
    
    Args:
        text: Raw MedGemma output text
        
    Returns:
        Cleaned and formatted text
    """
    if not text:
        return text
    
    # Remove multiple asterisks (markdown bold/italic)
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    
    # Remove remaining single asterisks
    text = re.sub(r'\*', '', text)
    
    # Remove markdown headers (##, ###, etc.)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    
    # Remove markdown links [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # Remove markdown code blocks ```
    text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
    
    # Remove inline code `text`
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Remove markdown horizontal rules (---, ***, ___)
    text = re.sub(r'^[-*_]{3,}$', '', text, flags=re.MULTILINE)
    
    # Remove excessive line breaks (more than 2 consecutive)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Remove empty lines at the beginning and end
    text = text.strip()
    
    # Fix spacing around punctuation
    text = re.sub(r'\s+([,.!?;:])', r'\1', text)
    text = re.sub(r'([,.!?;:])\s*([A-Z])', r'\1 \2', text)
    
    # Ensure proper sentence spacing
    text = re.sub(r'\.([A-Z])', r'. \1', text)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Clean up common markdown artifacts
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
    text = re.sub(r'_([^_]+)_', r'\1', text)        # Italic
    text = re.sub(r'~~([^~]+)~~', r'\1', text)      # Strikethrough
    
    # Remove bullet points and list markers
    text = re.sub(r'^[-•*+]\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)
    
    # Clean up any remaining formatting artifacts
    text = re.sub(r'[_~`]', '', text)
    
    return text.strip()