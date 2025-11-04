# 🏥 Dhanvantri Healthcare Chatbot - Setup Guide

Complete setup guide for the Dhanvantri multilingual healthcare education chatbot with voice capabilities.

## 📋 Prerequisites

### Required Software
- **Python 3.9+** - For backend and Whisper service
- **Node.js 16+** - For frontend React application
- **Git** - For version control

### Optional (Recommended)
- **Ollama** - For local LLM inference (MedGemma-4B)
- **FFmpeg** - For better audio processing

## 🚀 Quick Start

### 1. Clone and Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd Dhanvantri

# Make scripts executable
chmod +x start_services.sh stop_services.sh
```

### 2. Install Dependencies

#### Backend Dependencies
```bash
cd backend
pip3 install -r requirements.txt
cd ..
```

#### Whisper Service Dependencies
```bash
pip3 install -r whisper_requirements.txt
```

#### Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### 3. Start All Services
```bash
./start_services.sh
```

This will start:
- **Whisper Service**: http://localhost:5001
- **Backend API**: http://localhost:8000  
- **Frontend**: http://localhost:3000

### 4. Access the Application
Open your browser and go to: **http://localhost:3000**

## 🔧 Manual Setup (Alternative)

If you prefer to start services manually:

### Terminal 1: Whisper Service
```bash
python3 whisper_service.py
```

### Terminal 2: Backend API
```bash
cd backend
python3 -m uvicorn main:app --reload --port 8000
```

### Terminal 3: Frontend
```bash
cd frontend
npm run dev
```

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │ Whisper Service │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (Flask)       │
│   Port 3000     │    │   Port 8000     │    │   Port 5001     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Ollama LLM    │
                       │   (Optional)    │
                       │   Port 11434    │
                       └─────────────────┘
```

## 🎯 Features

### Core Features
- ✅ **Multilingual Support**: English, Hindi, Bengali, Bhojpuri, Kannada
- ✅ **Voice Input**: Browser-based and server-side speech recognition
- ✅ **Text-to-Speech**: Automatic response playback
- ✅ **Medical Context**: Disease information and health education
- ✅ **Emergency Detection**: Automatic emergency response for critical keywords
- ✅ **Real-time Chat**: Instant messaging interface

### Voice Capabilities
- **Browser STT**: Uses Web Speech API (Chrome/Edge recommended)
- **Server STT**: Uses OpenAI Whisper for better accuracy
- **TTS**: Browser-based text-to-speech in multiple languages
- **Audio Recording**: Direct microphone access for voice input

## 🔍 API Endpoints

### Backend API (Port 8000)
- `GET /` - Root endpoint with API info
- `GET /api/health` - Comprehensive health check
- `POST /api/chat` - Text-based chat
- `POST /api/chat/audio` - Audio file upload
- `POST /api/chat/audio-base64` - Base64 audio data
- `GET /api/chat/history` - Chat history
- `DELETE /api/chat/history` - Clear chat history

### Whisper Service (Port 5001)
- `GET /health` - Service health check
- `POST /transcribe` - Audio transcription
- `GET /models` - Available models

## 🛠️ Configuration

### Backend Configuration (`backend/config.py`)
```python
# Ollama Configuration
ollama_base: str = "http://localhost:11434"
model_name: str = "medgemma-4b"

# Whisper Configuration  
whisper_base: str = "http://localhost:5001"

# Application Configuration
port: int = 8000
cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]
```

### Environment Variables
Create `.env` file in the backend directory:
```env
OLLAMA_BASE=http://localhost:11434
WHISPER_BASE=http://localhost:5001
LOG_LEVEL=INFO
ENABLE_PRODUCTION_FEATURES=false
```

## 🧪 Testing

### Test Whisper Service
```bash
python3 test_whisper_service.py
```

### Test Backend Health
```bash
curl http://localhost:8000/api/health
```

### Test Frontend
Open http://localhost:3000 and try:
1. Text chat in different languages
2. Voice input (both browser and server modes)
3. Text-to-speech playback

## 🚨 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the port
lsof -i :5001  # or :8000, :3000

# Kill the process
kill -9 <PID>
```

#### Whisper Model Download
First run downloads the Whisper model (~139MB):
```bash
# This happens automatically on first transcription
# Wait for download to complete
```

#### CORS Issues
Ensure backend CORS settings include your frontend URL:
```python
cors_origins: list = ["http://localhost:3000"]
```

#### Audio Permissions
For voice input, ensure browser has microphone permissions:
- Chrome: Click the microphone icon in address bar
- Firefox: Allow microphone access when prompted

### Service Status Check
```bash
# Check if services are running
curl http://localhost:3000  # Frontend
curl http://localhost:8000/api/health  # Backend
curl http://localhost:5001/health  # Whisper
```

## 🛑 Stopping Services

### Using Script
```bash
./stop_services.sh
```

### Manual Stop
```bash
# Find and kill processes
ps aux | grep -E "(whisper_service|uvicorn|vite)"
kill <PID>
```

## 📚 Development

### Adding New Languages
1. Update `SUPPORTED_LANGUAGES` in `frontend/src/App.jsx`
2. Add language codes to `speechLanguageCodes` in `VoiceControls.jsx`
3. Update backend language support in utils

### Modifying UI
- Frontend styles: `frontend/src/App.css`
- Voice controls: `frontend/src/components/VoiceControls.css`

### Backend Changes
- API routes: `backend/routes/`
- Services: `backend/services/`
- Configuration: `backend/config.py`

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check this setup guide
2. Review the troubleshooting section
3. Check service logs for errors
4. Create an issue in the repository

---

**Happy Coding! 🏥💻**