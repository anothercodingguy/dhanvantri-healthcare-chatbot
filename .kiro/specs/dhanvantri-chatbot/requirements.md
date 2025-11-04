# Requirements Document

## Introduction

Dhanvantri is a multilingual, voice-enabled healthcare education chatbot designed for rural and semi-urban users. The system provides medical information through a locally hosted LLM, supports five languages, includes outbreak alert capabilities, and prioritizes user safety through deterministic emergency detection. The application runs entirely locally without external dependencies or databases.

## Glossary

- **Dhanvantri_System**: The complete healthcare education chatbot application
- **MedGemma_Engine**: The locally hosted medical LLM (Ollama → MedGemma-4B) that provides medical knowledge
- **Voice_Interface**: The speech-to-text and text-to-speech functionality using Web Speech API and local Whisper service
- **Whisper_Engine**: The local Whisper service for speech-to-text and translation (configurable via WHISPER_BASE)
- **Language_Module**: The component handling multilingual support for five languages through Whisper
- **RedFlag_Detector**: The deterministic emergency detection system that bypasses LLM for urgent cases
- **Data_Adapter**: The modular interface for data access with in-memory implementation and clear extension points for databases
- **Medical_Disclaimer**: The mandatory safety notice included with every response

## Requirements

### Requirement 1

**User Story:** As a rural healthcare seeker, I want to ask medical questions in my native language, so that I can understand health information clearly.

#### Acceptance Criteria

1. THE Dhanvantri_System SHALL support user input in English, Hindi, Bengali, Bhojpuri, and Kannada languages through the Whisper_Engine
2. THE Dhanvantri_System SHALL provide responses in the same language as the user input when Whisper_Engine supports translation
3. WHEN the Whisper_Engine is unavailable or does not support a language, THE Dhanvantri_System SHALL return a clear error message indicating translation is unavailable
4. THE Whisper_Engine SHALL handle speech-to-text conversion for all supported languages
5. IF Whisper_Engine cannot translate to the target language, THE Dhanvantri_System SHALL provide the response in English with a translation unavailable flag

### Requirement 2

**User Story:** As a user with limited literacy, I want to interact with the chatbot using voice, so that I can access medical information without typing.

#### Acceptance Criteria

1. WHEN a user activates voice input, THE Voice_Interface SHALL use Web Speech API for local capture and optionally send audio to Whisper_Engine for server-side processing
2. THE Voice_Interface SHALL provide text-to-speech output using browser speechSynthesis API for all system responses
3. THE Dhanvantri_System SHALL provide a toggle for users to choose between local browser STT and server-side Whisper processing
4. WHEN server-side Whisper is selected, THE Voice_Interface SHALL send base64-encoded audio to the backend
5. WHEN voice input fails or Whisper_Engine is unavailable, THE Dhanvantri_System SHALL provide clear error messages and fallback to text input

### Requirement 3

**User Story:** As a healthcare seeker, I want to receive accurate medical information, so that I can make informed decisions about my health.

#### Acceptance Criteria

1. WHEN a user asks a medical question, THE MedGemma_Engine SHALL provide evidence-based responses
2. THE Dhanvantri_System SHALL include the Medical_Disclaimer with every response
3. THE MedGemma_Engine SHALL operate entirely offline using local resources
4. THE Dhanvantri_System SHALL maintain response consistency for similar queries
5. WHEN the MedGemma_Engine cannot provide a confident answer, THE Dhanvantri_System SHALL recommend consulting healthcare professionals

### Requirement 4

**User Story:** As a user in a medical emergency, I want immediate guidance without delays, so that I can take appropriate urgent action.

#### Acceptance Criteria

1. WHEN a user input contains emergency keywords, THE RedFlag_Detector SHALL identify the emergency immediately
2. IF an emergency is detected, THEN THE Dhanvantri_System SHALL bypass the MedGemma_Engine and provide immediate emergency guidance
3. THE RedFlag_Detector SHALL operate using deterministic rules without LLM processing
4. THE Dhanvantri_System SHALL provide emergency contact information for urgent cases
5. WHEN emergency guidance is provided, THE Dhanvantri_System SHALL emphasize the need for immediate professional medical attention

### Requirement 5

**User Story:** As a developer, I want a modular and scalable system architecture, so that I can easily extend the system with databases and external services.

#### Acceptance Criteria

1. THE Data_Adapter SHALL provide a clear interface for data access operations
2. THE Dhanvantri_System SHALL use in-memory storage for demonstration with JSON seed data loaded at startup
3. THE Data_Adapter SHALL include clear extension points and documentation for integrating persistent databases
4. THE Dhanvantri_System SHALL maintain modular design allowing easy replacement of storage, translation, and LLM components
5. THE Dhanvantri_System SHALL include adapter interfaces with TODO comments indicating where to plug external services

### Requirement 6

**User Story:** As a user with limited internet connectivity, I want the chatbot to work completely offline, so that I can access medical information anytime.

#### Acceptance Criteria

1. THE Dhanvantri_System SHALL operate with local Ollama and Whisper services without internet connectivity requirements
2. THE Dhanvantri_System SHALL run locally without Docker or external container dependencies
3. THE MedGemma_Engine SHALL function entirely through local Ollama installation
4. THE Whisper_Engine SHALL operate through local Whisper service configured via WHISPER_BASE environment variable
5. WHEN the application starts, THE Dhanvantri_System SHALL load seed data from local JSON files and verify connectivity to local services

### Requirement 7

**User Story:** As a user, I want a simple and accessible interface, so that I can easily navigate and use the chatbot features.

#### Acceptance Criteria

1. THE Dhanvantri_System SHALL provide a minimal dark-themed user interface
2. THE Dhanvantri_System SHALL ensure interface accessibility for users with varying technical literacy
3. WHEN users interact with the interface, THE Dhanvantri_System SHALL provide clear visual feedback
4. THE Dhanvantri_System SHALL organize features logically for intuitive navigation
5. THE Dhanvantri_System SHALL maintain consistent interface behavior across all supported languages
### Requi
rement 8

**User Story:** As a system administrator, I want clear configuration and monitoring capabilities, so that I can deploy and maintain the system effectively.

#### Acceptance Criteria

1. THE Dhanvantri_System SHALL use environment variables for all configuration with sensible defaults
2. THE Dhanvantri_System SHALL provide health check endpoints that verify Ollama and Whisper service connectivity
3. THE Dhanvantri_System SHALL include comprehensive documentation for local development and scaling guidance
4. THE Dhanvantri_System SHALL provide structured logging and basic metrics endpoints for observability
5. THE Dhanvantri_System SHALL include clear error handling with meaningful HTTP status codes and JSON error responses