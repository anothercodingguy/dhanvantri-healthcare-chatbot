"""
In-memory data storage for Dhanvantri chatbot.
Loads and manages JSON seed data with basic keyword search functionality.
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DiseaseSnippet:
    """Data structure for disease facts with multilingual content."""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id", "")
        self.title = data.get("title", "")
        self.content_en = data.get("content_en", "")
        self.content_hi = data.get("content_hi")
        self.content_bn = data.get("content_bn")
        self.content_bho = data.get("content_bho")
        self.content_kn = data.get("content_kn")
        self.keywords = data.get("keywords", [])
        self.source = data.get("source", "")
    
    def get_content(self, language: str = "en") -> str:
        """Get content in specified language, fallback to English."""
        lang_map = {
            "en": self.content_en,
            "hi": self.content_hi,
            "bn": self.content_bn,
            "bho": self.content_bho,
            "kn": self.content_kn
        }
        return lang_map.get(language) or self.content_en
    
    def matches_keywords(self, query: str) -> bool:
        """Check if query matches any keywords (case-insensitive)."""
        query_lower = query.lower()
        return any(keyword.lower() in query_lower for keyword in self.keywords)


class ChatMessage:
    """Data structure for chat messages."""
    
    def __init__(self, message: str, language: str, is_user: bool, user_id: Optional[int] = None):
        self.id = f"{datetime.now().isoformat()}_{hash(message) % 10000}"
        self.user_id = user_id
        self.message = message
        self.language = language
        self.timestamp = datetime.now()
        self.is_user = is_user
        self.sources = []
        self.translation_unavailable = False


class User:
    """Data structure for users."""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id", 0)
        self.name = data.get("name", "")
        self.preferred_language = data.get("preferred_language", "en")
        self.created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))


class UserDocument:
    """Data structure for uploaded user documents."""
    
    def __init__(self, text: str, filename: str, doc_type: str, user_id: Optional[int] = None):
        self.id = f"{datetime.now().isoformat()}_{hash(filename) % 10000}"
        self.user_id = user_id
        self.filename = filename
        self.text = text
        self.doc_type = doc_type  # 'pdf', 'json'
        self.timestamp = datetime.now()


class InMemoryStorage:
    """In-memory storage manager for Dhanvantri chatbot data."""
    
    def __init__(self):
        self.disease_facts: List[DiseaseSnippet] = []
        self.users: List[User] = []
        self.chat_history: List[ChatMessage] = []
        self.documents: List[UserDocument] = []  # Store parsed documents
        self._loaded = False
    
    def load_seed_data(self, data_dir: str = "data") -> None:
        """Load seed data from JSON files."""
        try:
            # Load disease facts
            disease_facts_path = os.path.join(data_dir, "disease_facts.json")
            if os.path.exists(disease_facts_path):
                with open(disease_facts_path, 'r', encoding='utf-8') as f:
                    disease_data = json.load(f)
                    self.disease_facts = [DiseaseSnippet(item) for item in disease_data]
                    logger.info(f"Loaded {len(self.disease_facts)} disease facts")
            else:
                logger.warning(f"Disease facts file not found: {disease_facts_path}")
            
            # Load users
            users_path = os.path.join(data_dir, "users_seed.json")
            if os.path.exists(users_path):
                with open(users_path, 'r', encoding='utf-8') as f:
                    users_data = json.load(f)
                    self.users = [User(item) for item in users_data]
                    logger.info(f"Loaded {len(self.users)} users")
            else:
                logger.warning(f"Users file not found: {users_path}")
            
            self._loaded = True
            logger.info("Seed data loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading seed data: {e}")
            raise
    
    def search_medical_context(self, query: str, limit: int = 5) -> List[DiseaseSnippet]:
        """Basic keyword search for medical context."""
        if not self._loaded:
            logger.warning("Seed data not loaded, call load_seed_data() first")
            return []
        
        matches = []
        for fact in self.disease_facts:
            if fact.matches_keywords(query):
                matches.append(fact)
                if len(matches) >= limit:
                    break
        
        logger.debug(f"Found {len(matches)} medical context matches for query: {query}")
        return matches
    
    def add_chat_message(self, message: str, language: str, is_user: bool, user_id: Optional[int] = None) -> ChatMessage:
        """Add a chat message to history."""
        chat_msg = ChatMessage(message, language, is_user, user_id)
        self.chat_history.append(chat_msg)
        logger.debug(f"Added chat message: {chat_msg.id}")
        return chat_msg
    
    def get_chat_history(self, user_id: Optional[int] = None, limit: int = 50) -> List[ChatMessage]:
        """Get chat history, optionally filtered by user."""
        if user_id is not None:
            history = [msg for msg in self.chat_history if msg.user_id == user_id]
        else:
            history = self.chat_history
        
        # Return most recent messages first
        return sorted(history, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        for user in self.users:
            if user.id == user_id:
                return user
        return None
    
    def clear_chat_history(self) -> None:
        """Clear all chat history (useful for testing/reset)."""
        self.chat_history.clear()
        logger.info("Chat history cleared")

    def add_document(self, text: str, filename: str, doc_type: str, user_id: Optional[int] = None) -> UserDocument:
        """Add a parsed document to storage."""
        doc = UserDocument(text, filename, doc_type, user_id)
        self.documents.append(doc)
        logger.info(f"Stored document: {filename} for user {user_id}")
        return doc

    def get_user_documents(self, user_id: int) -> List[UserDocument]:
        """Get all documents for a specific user."""
        # For demo purposes, if user_id is None or 0, return all (or simple logic)
        # Assuming simple single-user demo for now if user_id is not strictly managed.
        if user_id is None: 
            return self.documents 
        return [doc for doc in self.documents if doc.user_id == user_id or doc.user_id is None]


# Global storage instance
storage = InMemoryStorage()


def get_storage() -> InMemoryStorage:
    """Get the global storage instance."""
    return storage


def initialize_storage(data_dir: str = "data") -> None:
    """Initialize storage with seed data."""
    storage.load_seed_data(data_dir)