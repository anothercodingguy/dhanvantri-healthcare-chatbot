# Dhanvantri Healthcare Chatbot

A multilingual, voice-enabled healthcare education chatbot designed for rural and semi-urban users. Dhanvantri provides medical information through the Groq Cloud API (Llama 3.3), supports five languages (English, Hindi, Bengali, Bhojpuri, Kannada), and includes voice interaction capabilities for accessibility.

## Features

- **Multilingual Support**: Automatic translation between 5 supported languages
- **Voice Interface**: Speech-to-text and text-to-speech for accessibility
- **Medical Knowledge**: Powered by Groq Llama 3.3 for evidence-based responses
- **Fast Inference**: Uses Groq's high-performance inference engine
- **Accessibility**: Dark theme UI designed for users with varying technical literacy
- **Safety**: Medical disclaimer included with every response

## Architecture

1. **Frontend**: React (Vite) app with voice controls and dark UI
2. **Backend**: FastAPI with chat endpoint and health checks  
3. **Services**: Groq Cloud API for LLM and Whisper (STT)

## Project Structure

```
dhanvantri-chatbot/
├── backend/                 # FastAPI backend
│   ├── main.py             # Application entry point
│   ├── config.py           # Configuration management
│   ├── routes/             # API route handlers
│   └── services/           # External service clients (Groq)
├── frontend/               # React frontend
│   ├── src/                # Source code
│   └── vite.config.js      # Vite build configuration
├── start_services.sh       # Script to start local dev environment
└── stop_services.sh        # Script to stop services
```

## Prerequisites

- **Python 3.9+**
- **Node.js 16+**
- **Groq API Key**: Get one from [console.groq.com](https://console.groq.com)

## Quick Start (Local Development)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd dhanvantri-chatbot
   ```

2. **Setup Environment Variables**:
   Copy `.env.example` to `.env` and add your Groq API Key:
   ```bash
   cp .env.example .env
   # Edit .env and set GROQ_API_KEY=your_key_here
   ```

3. **Install Dependencies & Start Services**:
   The `start_services.sh` script will check for dependencies, install them if missing, and start both backend and frontend.
   ```bash
   chmod +x start_services.sh
   ./start_services.sh
   ```

4. **Access the Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Health check: http://localhost:8000/api/health

## Configuration

Environment variables in `.env`:

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | **Required**. API key for Groq Cloud. |
| `MODEL_NAME` | Helper model (Default: `llama-3.3-70b-versatile`) |
| `PORT` | Backend port (Default: `8000`) |
| `LOG_LEVEL` | Logging level (Default: `INFO`) |

## Deployment

### Deploy to Render

1. **Push to GitHub**:
   ```bash
   git push origin main
   ```

2. **Create Service on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com).
   - Click **New +** -> **Web Service**.
   - Connect your GitHub repo.
   - Render should auto-detect the configuration from `render.yaml` (if present) or you can choose "Python 3".
   - **Build Command**: `pip install -r backend/requirements.txt && cd frontend && npm install && npm run build`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables on Render**:
   - `GROQ_API_KEY`: Your Groq API Key
   - `PYTHON_VERSION`: `3.9.0` (or greater)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Medical Disclaimer

This chatbot is for educational purposes only and should not replace professional medical advice. Always consult with qualified healthcare providers for medical concerns.