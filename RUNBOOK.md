# Dhanvantri Chatbot - Development Runbook

This runbook provides exact step-by-step instructions for local development and deployment of the Dhanvantri healthcare chatbot.

## Prerequisites Verification

Before starting, verify you have the required software installed:

```bash
# Check Python version (3.8+ required)
python --version

# Check Node.js version (16+ required)
node --version

# Check npm version
npm --version

# Check if Ollama is installed
ollama --version
```

## Initial Setup

### 1. Environment Configuration

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your configuration:
   ```bash
   # Required settings
   OLLAMA_BASE=http://localhost:11434
   MODEL_NAME=medgemma:4b
   
   # Optional settings
   WHISPER_BASE=http://localhost:5000
   PORT=8000
   LOG_LEVEL=INFO
   ENABLE_PRODUCTION_FEATURES=false
   ```

### 2. Ollama Setup

1. Install Ollama (if not already installed):
   - macOS: `brew install ollama`
   - Linux: `curl -fsSL https://ollama.ai/install.sh | sh`
   - Windows: Download from https://ollama.ai

2. Start Ollama service:
   ```bash
   ollama serve
   ```

3. Pull the MedGemma-4B model:
   ```bash
   ollama pull medgemma:4b
   ```

4. Verify model installation:
   ```bash
   ollama list
   # Should show medgemma:4b in the list
   ```

5. Test model functionality:
   ```bash
   ollama run medgemma:4b "What is diabetes?"
   ```

### 3. Whisper Setup (Optional)

If you want server-side speech-to-text processing:

1. Install Whisper:
   ```bash
   pip install openai-whisper
   ```

2. Create a simple Whisper service (example):
   ```python
   # whisper_service.py
   from flask import Flask, request, jsonify
   import whisper
   import base64
   import io
   
   app = Flask(__name__)
   model = whisper.load_model("base")
   
   @app.route('/transcribe', methods=['POST'])
   def transcribe():
       audio_data = request.json['audio']
       audio_bytes = base64.b64decode(audio_data)
       # Process audio and return transcription
       return jsonify({"text": "transcribed text"})
   
   if __name__ == '__main__':
       app.run(port=5000)
   ```

3. Run Whisper service:
   ```bash
   python whisper_service.py
   ```

## Development Workflow

### Backend Development

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the backend server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

5. Verify backend is running:
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

### Frontend Development

1. Open a new terminal and navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Access the application:
   - Frontend: http://localhost:5173
   - Backend API docs: http://localhost:8000/docs

## Testing the Application

### Automated Integration Testing

The project includes comprehensive integration testing tools:

#### 1. Integration Verification (Static Analysis)
```bash
# Verify component wiring and configuration
python3 verify_integration.py
```

This checks:
- File structure completeness
- Python import dependencies
- Configuration files validity
- Data file formatting
- API route definitions
- Frontend component integration

#### 2. Live Integration Testing (Requires Running Services)
```bash
# Test end-to-end functionality with running services
python3 test_integration.py

# Test with custom backend URL
python3 test_integration.py --url http://localhost:8001

# Save results to file
python3 test_integration.py --output test_results.json
```

This tests:
- Backend health endpoints
- Service dependencies (Ollama, Whisper)
- Chat functionality with text input
- Multilingual conversation flow
- Error handling for invalid requests

### Manual Testing

#### 1. Basic Functionality Test

1. Open http://localhost:5173 in your browser
2. Select a language from the dropdown
3. Type a simple medical question: "What is fever?"
4. Verify you receive a response with medical disclaimer

#### 2. Voice Functionality Test

1. Click the microphone button
2. Allow microphone permissions when prompted
3. Speak a medical question clearly
4. Verify transcription appears and response is generated
5. Check if text-to-speech plays the response

#### 3. Multilingual Test

1. Select Hindi from language dropdown
2. Type: "मधुमेह क्या है?" (What is diabetes?)
3. Verify response is in Hindi (if Whisper is available)
4. Test other supported languages similarly

#### 4. Error Handling Test

1. Stop Ollama service: `ollama stop`
2. Try sending a message
3. Verify appropriate error message is displayed
4. Restart Ollama: `ollama serve`

#### 5. Voice Mode Testing

1. Toggle between "Browser STT" and "Server STT" modes
2. Test voice input in both modes
3. Verify different behavior:
   - Browser STT: Uses Web Speech API locally
   - Server STT: Records audio and sends to Whisper service
4. Test text-to-speech output in different languages

#### 6. Service Dependency Testing

1. Test with only Ollama running (Whisper stopped):
   - Voice input should fallback to browser STT
   - Text chat should work normally
   - Translation features may be limited

2. Test with both services running:
   - Full multilingual support
   - Server-side speech processing available
   - All features functional

## API Testing

### Health Check
```bash
curl -X GET http://localhost:8000/health
```

### Chat Endpoint (Text)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is diabetes?",
    "language": "en"
  }'
```

### Chat Endpoint (Audio)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "audio_data": "base64_encoded_audio_data",
    "language": "en"
  }'
```

## Common Development Tasks

### Adding New Medical Content

1. Edit `data/disease_facts.json`
2. Add new entries following the existing structure:
   ```json
   {
     "id": "unique_id",
     "title": "Condition Name",
     "content_en": "English content...",
     "content_hi": "Hindi content...",
     "keywords": ["keyword1", "keyword2"],
     "source": "Medical Source"
   }
   ```
3. Restart backend to reload data

### Modifying UI Components

1. Edit files in `frontend/src/components/`
2. Changes are automatically hot-reloaded
3. Check browser console for any errors

### Adding New API Endpoints

1. Create new route file in `backend/routes/`
2. Import and include in `backend/main.py`
3. Update API documentation

## Troubleshooting Guide

### Backend Issues

**Issue**: `ModuleNotFoundError` when starting backend
```bash
# Solution: Ensure virtual environment is activated and dependencies installed
source venv/bin/activate
pip install -r requirements.txt
```

**Issue**: Ollama connection failed
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama if not running
ollama serve

# Verify model is available
ollama list
```

**Issue**: Port already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process (replace PID)
kill -9 <PID>

# Or use different port
uvicorn main:app --reload --port 8001
```

### Frontend Issues

**Issue**: `npm install` fails
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Issue**: CORS errors in browser
- Ensure backend is running on port 8000
- Check CORS configuration in `backend/main.py`
- Verify frontend is accessing correct backend URL

**Issue**: Voice features not working
- Check browser permissions for microphone
- Ensure HTTPS or localhost (required for Web Speech API)
- Verify Whisper service is running (if using server-side STT)

### Service Integration Issues

**Issue**: Whisper service unavailable
- Application will fallback to browser STT
- Check `WHISPER_BASE` URL in `.env`
- Verify Whisper service is running on correct port

**Issue**: Model responses are slow
- MedGemma-4B requires significant computational resources
- Consider using smaller model for development: `ollama pull medgemma:2b`
- Monitor system resources during operation

## Production Deployment Notes

### Environment Variables for Production

```bash
# Production settings
ENABLE_PRODUCTION_FEATURES=true
LOG_LEVEL=WARNING
PORT=80

# Security considerations
# - Use HTTPS in production
# - Configure proper CORS origins
# - Set up proper logging and monitoring
```

### Performance Considerations

1. **Model Selection**: MedGemma-4B requires ~8GB RAM
2. **Concurrent Users**: Consider load balancing for multiple users
3. **Storage**: In-memory storage is not persistent - consider database integration
4. **Monitoring**: Implement proper health checks and metrics

### Security Checklist

- [ ] Configure HTTPS/TLS certificates
- [ ] Set up proper CORS origins (not wildcard)
- [ ] Implement rate limiting
- [ ] Add input validation and sanitization
- [ ] Set up proper logging (no sensitive data)
- [ ] Configure firewall rules
- [ ] Regular security updates

## Development Best Practices

1. **Code Organization**: Follow existing module structure
2. **Error Handling**: Always include proper error responses
3. **Logging**: Use structured logging with appropriate levels
4. **Documentation**: Update this runbook when adding features
5. **Testing**: Test multilingual functionality thoroughly
6. **Medical Content**: Verify medical information accuracy
7. **Accessibility**: Ensure UI works with screen readers

## Useful Commands Reference

```bash
# Backend
cd backend && uvicorn main:app --reload --port 8000
cd backend && python -m pytest  # If tests are added later

# Frontend  
cd frontend && npm run dev
cd frontend && npm run build
cd frontend && npm run preview

# Services
ollama serve
ollama list
ollama pull medgemma:4b

# Health checks
curl http://localhost:8000/health
curl http://localhost:5173  # Frontend health

# Logs
tail -f backend/logs/app.log  # If logging to file
```

This runbook should be updated as the project evolves and new features are added.