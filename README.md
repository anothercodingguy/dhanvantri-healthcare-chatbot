# Dhanvantri Healthcare Chatbot

A multilingual, voice-enabled healthcare education chatbot designed for rural and semi-urban users. Dhanvantri provides medical information through a locally hosted LLM, supports five languages (English, Hindi, Bengali, Bhojpuri, Kannada), and includes voice interaction capabilities for accessibility.

## Features

- **Multilingual Support**: Automatic translation between 5 supported languages
- **Voice Interface**: Speech-to-text input and text-to-speech output
- **Medical Knowledge**: Powered by MedGemma-4B LLM for evidence-based responses
- **Offline Operation**: Runs completely locally without internet dependencies
- **Accessibility**: Dark theme UI designed for users with varying technical literacy
- **Safety**: Medical disclaimer included with every response

## Architecture

The system uses a simple 3-layer architecture:

1. **Frontend**: React app with voice controls and dark UI
2. **Backend**: FastAPI with chat endpoint and health checks  
3. **Services**: Local Ollama (MedGemma-4B) and Whisper for LLM and translation

## Project Structure

```
dhanvantri-chatbot/
├── backend/                 # FastAPI backend
│   ├── main.py             # Application entry point
│   ├── config.py           # Configuration management
│   ├── routes/             # API route handlers
│   │   ├── chat.py         # Chat endpoint with audio/text support
│   │   └── health.py       # Health check endpoints
│   ├── services/           # External service clients
│   │   ├── ollama_client.py    # Ollama/MedGemma integration
│   │   └── whisper_client.py   # Whisper STT/translation
│   ├── data/               # Data layer and storage
│   │   └── in_memory.py    # In-memory data management
│   ├── utils/              # Utility functions
│   │   └── utils.py        # Medical disclaimer and helpers
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.jsx         # Main chat interface
│   │   └── components/     # React components
│   │       └── VoiceControls.jsx  # Voice input/output
│   ├── public/             # Static assets
│   ├── package.json        # Node.js dependencies
│   └── vite.config.js      # Vite build configuration
├── data/                   # Seed data files
│   ├── disease_facts.json  # Medical information in multiple languages
│   └── users_seed.json     # Demo user data
└── .env.example            # Environment variables template
```

## Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Ollama** with MedGemma-4B model installed locally
- **Whisper service** (optional, for server-side STT)

### Installing Ollama and MedGemma-4B

1. Install Ollama from [https://ollama.ai](https://ollama.ai)
2. Pull the MedGemma-4B model:
   ```bash
   ollama pull medgemma:4b
   ```
3. Verify installation:
   ```bash
   ollama list
   ```

### Installing Whisper Service (Optional)

For server-side speech-to-text processing:

1. Install OpenAI Whisper:
   ```bash
   pip install openai-whisper
   ```
2. Run Whisper service on port 5000 (implementation depends on your setup)

## Quick Start

### 🚀 One-Command Deployment (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd dhanvantri-chatbot

# Deploy with Docker (includes all services)
./deploy.sh deploy development
```

**Access the application:**
- Frontend & API: http://localhost:8000
- Health check: http://localhost:8000/api/health

### 📋 Manual Setup (Development)

1. **Clone and setup environment**:
   ```bash
   git clone <repository-url>
   cd dhanvantri-chatbot
   cp .env.example .env
   ```

2. **Configure environment variables** in `.env`:
   ```bash
   # Required
   OLLAMA_BASE=http://localhost:11434
   MODEL_NAME=alibayram/medgemma:4b
   
   # Optional
   WHISPER_BASE=http://localhost:5001
   PORT=8000
   LOG_LEVEL=INFO
   ```

3. **Install backend dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies**:
   ```bash
   cd ../frontend
   npm install
   ```

5. **Start services using the provided script**:
   ```bash
   ./start_services.sh
   ```

6. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Whisper Service: http://localhost:5001
   - Health check: http://localhost:8000/api/health

### 🏭 Production Deployment

For production deployment with Docker, SSL, and monitoring:

```bash
# Production deployment
./deploy.sh deploy production

# Access via reverse proxy
# HTTP: http://your-domain
# HTTPS: https://your-domain (after SSL setup)
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete production setup guide.

## Usage

### Text Chat
1. Open the application in your browser
2. Select your preferred language from the dropdown
3. Type your medical question in the chat input
4. Receive responses with medical disclaimer

### Voice Chat
1. Click the microphone button to start voice input
2. Speak your question in any supported language
3. The system will transcribe, process, and respond
4. Responses are played back using text-to-speech

### Supported Languages
- English (en)
- Hindi (hi) - हिंदी
- Bengali (bn) - বাংলা
- Bhojpuri (bho) - भोজপুরী
- Kannada (kn) - ಕನ್ನಡ

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE` | `http://localhost:11434` | Ollama service URL |
| `MODEL_NAME` | `medgemma:4b` | LLM model name |
| `WHISPER_BASE` | `http://localhost:5000` | Whisper service URL (optional) |
| `PORT` | `8000` | Backend server port |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ENABLE_PRODUCTION_FEATURES` | `false` | Enable production features |

### Service Dependencies

The application requires these local services:

1. **Ollama**: Must be running with MedGemma-4B model
2. **Whisper** (optional): For server-side speech processing

Check service status at: http://localhost:8000/health

## Development

### Backend Development
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Common Issues

1. **Ollama connection failed**:
   - Ensure Ollama is running: `ollama serve`
   - Check model is available: `ollama list`
   - Verify OLLAMA_BASE URL in .env

2. **Whisper service unavailable**:
   - Whisper is optional for basic functionality
   - App will use browser STT when Whisper unavailable
   - Check WHISPER_BASE URL if using server-side STT

3. **Frontend build errors**:
   - Ensure Node.js 16+ is installed
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`

4. **CORS errors**:
   - Backend includes CORS middleware for localhost development
   - Check frontend is running on expected port (5173)

### Health Checks

Monitor service health at `/health` endpoint:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "ollama": "connected",
    "whisper": "connected"
  }
}
```

## 🚀 Deployment

### ☁️ Cloud Deployment (Recommended)

#### Deploy to Render.com
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/your-username/dhanvantri-chatbot)

**One-click deployment to Render:**
- ✅ **Zero DevOps**: No infrastructure management needed
- ✅ **Auto-scaling**: Automatically scales based on traffic
- ✅ **Free SSL**: HTTPS certificates included
- ✅ **Git Integration**: Deploy directly from GitHub
- ✅ **Cost-effective**: Starting at $7/month
- ✅ **Built-in Monitoring**: Health checks and metrics included

### 🛠️ Local Development

For local development and testing:

```bash
# Start all services
./start_services.sh

# Stop all services  
./stop_services.sh
```

### Key Features
- ✅ **Cloud-Ready**: Optimized for Render deployment
- ✅ **Production Ready**: Auto-scaling, SSL, health monitoring
- ✅ **Secure**: CORS protection, input validation, security headers
- ✅ **Scalable**: Handles multiple concurrent users
- ✅ **Accessible**: Voice interface and multilingual support

### Documentation
- 🌐 [Render Deployment Guide](RENDER_DEPLOYMENT.md) - Complete setup instructions
- 🔧 [Development Runbook](RUNBOOK.md) - Local development workflow
- ⚙️ [Setup Guide](SETUP_GUIDE.md) - Initial setup and configuration

## Contributing

1. Follow the existing code structure and patterns
2. Add appropriate error handling and logging
3. Update documentation for new features
4. Test multilingual functionality when making changes
5. Ensure Docker builds pass: `docker build -t dhanvantri .`
6. Run health checks: `./deploy.sh health`

## License

[Add your license information here]

## Medical Disclaimer

This chatbot is for educational purposes only and should not replace professional medical advice. Always consult with qualified healthcare providers for medical concerns.