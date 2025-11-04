# Implementation Plan

- [x] 1. Set up project structure and configuration
  - Create directory structure for backend and frontend
  - Set up environment configuration with typed settings
  - Create .env.example with all required variables
  - _Requirements: 6.2, 6.3, 8.1_

- [x] 2. Implement external service clients
- [x] 2.1 Create Ollama client for MedGemma-4B integration
  - Write ollama_client.py with chat function and retry logic
  - Implement system prompt construction for medical conversations
  - Add error handling for Ollama service connectivity
  - _Requirements: 3.1, 3.3, 3.4_

- [x] 2.2 Create Whisper client for STT and translation
  - Write whisper_client.py with transcribe_audio_bytes function
  - Implement translate_text function for language conversion
  - Add proper error handling for unsupported languages
  - _Requirements: 1.3, 1.5, 2.1, 2.5_

- [x] 3. Implement data layer and utilities
- [x] 3.1 Create in-memory data storage
  - Write in_memory.py for loading and managing JSON seed data
  - Implement basic keyword search for medical context
  - Create data structures for disease facts and chat history
  - _Requirements: 6.5, 5.2_

- [x] 3.2 Implement utility functions
  - Write utils.py with medical disclaimer appending
  - Create system prompt construction helpers
  - Add basic text processing functions
  - _Requirements: 3.2, 8.5_

- [x] 4. Build FastAPI backend
- [x] 4.1 Create main application and health endpoints
  - Write main.py with FastAPI app initialization
  - Implement health.py route with service connectivity checks
  - Add structured logging and basic metrics
  - _Requirements: 8.2, 8.4_

- [x] 4.2 Implement chat API endpoint
  - Write chat.py route handling text and audio input
  - Implement core conversation flow with translation
  - Add proper error responses and status codes
  - _Requirements: 1.1, 1.2, 2.1, 3.1, 8.5_

- [x] 5. Build React frontend
- [x] 5.1 Create main application interface
  - Write App.jsx with dark theme chat interface
  - Implement language selector and message display
  - Add error handling and user feedback
  - _Requirements: 7.1, 7.3, 7.4, 7.5_

- [x] 5.2 Implement voice controls component
  - Write VoiceControls.jsx with Web Speech API integration
  - Add audio recording and base64 encoding for server-side Whisper
  - Implement text-to-speech output with language-specific voices
  - Create toggle between local and server-side speech processing
  - _Requirements: 2.1, 2.2, 2.4, 2.5_

- [x] 6. Create seed data and documentation
- [x] 6.1 Generate medical seed data
  - Create disease_facts.json with medical information in multiple languages
  - Create users_seed.json with demo user data
  - Ensure proper JSON structure for easy loading
  - _Requirements: 5.2, 6.5_

- [x] 6.2 Write comprehensive documentation
  - Create README.md with project overview and setup instructions
  - Write RUNBOOK.md with exact local development steps
  - Document environment variables and configuration
  - _Requirements: 8.3_

- [x] 7. Add deployment helpers and final integration
- [x] 7.1 Create deployment scripts
  - Write git_push.sh helper script for repository management
  - Add package.json and requirements.txt with all dependencies
  - Create vite.config.js for frontend build configuration
  - _Requirements: 6.2, 8.3_

- [x] 7.2 Final integration and testing
  - Wire together all components and verify end-to-end functionality
  - Test multilingual conversation flow with voice input/output
  - Verify error handling when services are unavailable
  - _Requirements: 1.1, 1.2, 2.1, 2.2, 3.1, 8.2_