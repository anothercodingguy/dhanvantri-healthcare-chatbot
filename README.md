# 🏥 Dhanvantri AI - Healthcare Assistant

> **AI-powered multilingual healthcare education platform for rural and semi-urban users**

Dhanvantri AI is a comprehensive healthcare chatbot that combines advanced AI capabilities with accessible interfaces to provide medical information and support. Built with FastAPI and React, it features voice interaction, document analysis, medical image recognition, and real-time health news updates.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 16+](https://img.shields.io/badge/node-16+-green.svg)](https://nodejs.org/)

---

## ✨ Features

### 🗣️ **Voice-to-Voice Interaction**
- **Speech-to-Text**: Convert spoken queries to text using Web Speech API
- **Text-to-Speech**: Neural voice synthesis for natural-sounding responses
- **Voice-to-Voice Mode**: Seamless conversation flow with automatic TTS for voice inputs
- **Multi-accent Support**: Works across different regional accents

### 🌍 **Multilingual Support**
- **5 Languages**: English, Hindi, Bengali, Bhojpuri, and Kannada
- **Automatic Translation**: Real-time translation of medical information
- **Language-Aware STT/TTS**: Speech recognition adapts to selected language
- **Native Script Display**: Full Unicode support for regional scripts

### 🤖 **AI-Powered Medical Assistance**
- **Groq Llama 3.3 70B**: High-performance medical knowledge base
- **Context-Aware Responses**: Maintains conversation history
- **Medical Disclaimer**: Built-in safety warnings with every response
- **Emergency Detection**: Identifies urgent medical situations

### 📄 **Document Analysis**
- **PDF Processing**: Upload and analyze medical reports, prescriptions, lab results
- **JSON Support**: Import structured health data
- **Text Extraction**: Intelligent parsing using PyPDF
- **Q&A on Documents**: Ask questions about uploaded medical documents

### 🖼️ **Medical Image Analysis**
- **Image Upload**: Support for medical scans, prescription images, rashes, etc.
- **AI Vision Analysis**: Provide preliminary insights on medical images
- **Multi-Format Support**: JPEG, PNG, and common image formats

### 📰 **Health News Integration**
- **Real-Time News**: Fetch latest health news from NewsData.io API
- **Country-Specific**: Filter by region (default: India)
- **Multi-Language News**: News in 5 supported languages
- **Curated Health Content**: Focus on medical and wellness topics

### 🎨 **Modern User Interface**
- **Dark Theme**: Eye-friendly interface with medical-inspired aesthetics
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-Time Status**: Connection health monitoring
- **Message History**: View past conversations with timestamps
- **Source Citations**: Transparent sourcing of information

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  - Voice Controls (Speech API)                           │
│  - Multilingual UI                                       │
│  - Document/Image Upload                                 │
│  - News Modal                                            │
└───────────────────┬─────────────────────────────────────┘
                    │ REST API
┌───────────────────▼─────────────────────────────────────┐
│                Backend (FastAPI)                         │
│  ┌─────────────┬──────────────┬────────────────────┐    │
│  │ Chat Routes │ News Routes  │ Document Routes    │    │
│  └─────────────┴──────────────┴────────────────────┘    │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┼──────────────┐
        │           │              │
┌───────▼─────┐ ┌──▼──────┐ ┌─────▼──────┐
│   Groq API  │ │NewsData │ │  In-Memory │
│  (Llama 3.3)│ │   API   │ │  Storage   │
└─────────────┘ └─────────┘ └────────────┘
```

---

## 📁 Project Structure

```
Dhanvantri/
│
├── backend/                      # FastAPI Backend
│   ├── main.py                   # Application entry point
│   ├── config.py                 # Configuration management
│   │
│   ├── routes/                   # API Routes
│   │   ├── chat.py               # Chat endpoints (text, audio, image)
│   │   ├── health.py             # Health check endpoints
│   │   ├── news.py               # News fetching endpoints
│   │   └── documents.py          # Document upload and analysis
│   │
│   ├── services/                 # External Services
│   │   └── groq_client.py        # Groq API client
│   │
│   ├── data/                     # Data Management
│   │   └── in_memory.py          # In-memory storage
│   │
│   ├── utils/                    # Utilities
│   │   ├── parser.py             # Document parser
│   │   └── utils.py              # Helper functions
│   │
│   └── requirements.txt          # Python dependencies
│
├── frontend/                     # React Frontend
│   ├── src/
│   │   ├── App.jsx               # Main application component
│   │   ├── App.css               # Styling
│   │   ├── NewsModal.jsx         # News modal component
│   │   └── utils/
│   │       └── VoiceManager.js   # Client-side TTS manager
│   │
│   ├── public/                   # Static assets
│   ├── package.json              # Node dependencies
│   └── vite.config.js            # Vite configuration
│
├── .env.example                  # Environment variables template
├── start_services.sh             # Development startup script
├── stop_services.sh              # Development shutdown script
├── render-entrypoint.sh          # Production entrypoint for Render
├── Dockerfile.render             # Docker configuration for Render
└── README.md                     # This file
```

---

## 🚀 Quick Start

### **Prerequisites**

- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **Groq API Key** - Get from [console.groq.com](https://console.groq.com)
- **NewsData API Key** (optional) - Get from [newsdata.io](https://newsdata.io)

### **Installation**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/dhanvantri.git
   cd dhanvantri
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   # Required
   GROQ_API_KEY=your_groq_api_key_here
   
   # Optional
   NEWS_API_KEY=your_newsdata_api_key_here
   ```

3. **Start the application**:
   ```bash
   chmod +x start_services.sh
   ./start_services.sh
   ```

   This script will:
   - Check for Python and Node.js
   - Install backend dependencies (if needed)
   - Install frontend dependencies (if needed)
   - Start the backend on port 8000
   - Start the frontend on port 3000

4. **Access the application**:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/api/health

### **Stopping Services**

```bash
./stop_services.sh
```

Or press `Ctrl+C` in the terminal where services are running.

---

## ⚙️ Configuration

### **Environment Variables**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | ✅ Yes | - | API key for Groq Cloud (Llama 3.3) |
| `NEWS_API_KEY` | ❌ No | - | NewsData.io API key for health news |
| `PORT` | ❌ No | `8000` | Backend server port |
| `LOG_LEVEL` | ❌ No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `CORS_ORIGINS` | ❌ No | `http://localhost:3000` | Allowed CORS origins (comma-separated) |
| `ENABLE_PRODUCTION_FEATURES` | ❌ No | `false` | Enable production optimizations |
| `MODEL_TEMPERATURE` | ❌ No | `0.7` | LLM temperature (0.0-1.0) |
| `MODEL_MAX_TOKENS` | ❌ No | `512` | Maximum tokens in LLM response |

### **Supported Languages**

| Code | Language | Script |
|------|----------|--------|
| `en` | English | Latin |
| `hi` | Hindi | Devanagari (हिंदी) |
| `bn` | Bengali | Bengali (বাংলা) |
| `bho` | Bhojpuri | Devanagari (भोजपुरी) |
| `kn` | Kannada | Kannada (ಕನ್ನಡ) |

---

## 🌐 API Endpoints

### **Chat Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Send text message |
| `POST` | `/api/chat/audio-base64` | Send audio message (base64) |
| `POST` | `/api/chat/image` | Analyze medical image |

### **Document Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/documents/upload` | Upload PDF/JSON document |

### **News Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/news/health` | Get health news (with country/language params) |
| `GET` | `/api/news/health/latest` | Get latest 10 health news articles |

### **Health Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | System health check |

---

## 🔧 Development

### **Backend Development**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### **Frontend Development**

```bash
cd frontend
npm install
npm run dev
```

### **Running Tests**

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### **Code Formatting**

```bash
# Backend (Black)
cd backend
black .

# Frontend (Prettier)
cd frontend
npm run format
```

---

## 🚢 Deployment

### **Deploy to Render**

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create Web Service on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click **New +** → **Web Service**
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`

3. **Set Environment Variables** on Render:
   - `GROQ_API_KEY` - Your Groq API key
   - `NEWS_API_KEY` - Your NewsData API key (optional)
   - `ENABLE_PRODUCTION_FEATURES` - `true`
   - `PYTHON_VERSION` - `3.9` or higher

4. **Deploy**:
   - Render will automatically build and deploy using `Dockerfile.render`
   - Access your app at `https://your-app.onrender.com`

### **Docker Deployment**

```bash
# Build the image
docker build -f Dockerfile.render -t dhanvantri .

# Run the container
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e NEWS_API_KEY=your_news_key \
  dhanvantri
```

---

## 🔒 Security Considerations

- **API Keys**: Never commit `.env` file to version control
- **Rate Limiting**: Implement rate limiting for production deployments
- **Input Validation**: All user inputs are validated server-side
- **CORS**: Configure CORS origins for production
- **Medical Disclaimer**: Always shown to prevent medical liability

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### **Code Style**

- **Python**: Follow PEP 8, use Black formatter
- **JavaScript**: Use ESLint and Prettier
- **Commits**: Use conventional commit messages

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Medical Disclaimer

**IMPORTANT**: Dhanvantri AI is designed for **educational and informational purposes only**. It is **NOT** a substitute for professional medical advice, diagnosis, or treatment.

- ❌ Do not use for medical emergencies
- ❌ Do not replace doctor consultations
- ❌ Do not rely solely on AI for medical decisions
- ✅ Always consult qualified healthcare professionals
- ✅ Seek immediate medical attention for emergencies

The information provided by this chatbot should not be considered as medical advice. Always consult with qualified healthcare providers for any medical concerns.

---

## 🙏 Acknowledgments

- **Groq** - For lightning-fast Llama 3.3 inference
- **NewsData.io** - For comprehensive health news API
- **FastAPI** - For the robust backend framework
- **React & Vite** - For the modern frontend stack
- **Web Speech API** - For voice recognition capabilities

---

## 📧 Contact

For questions, feedback, or support:

- **GitHub Issues**: [Create an issue](https://github.com/yourusername/dhanvantri/issues)

---

<div align="center">

**Built with ❤️ for accessible healthcare**

⭐ **Star this repo if you find it helpful!** ⭐

</div>