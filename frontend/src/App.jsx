import React, { useState, useEffect, useRef } from 'react';
// Voice controls integrated directly into the chat input
import './App.css';
import NewsModal from './NewsModal';
import { voiceManager } from './utils/VoiceManager';

const SUPPORTED_LANGUAGES = {
  'en': 'English',
  'hi': 'हिंदी (Hindi)',
  'bn': 'বাংলা (Bengali)',
  'bho': 'भोजपुरी (Bhojpuri)',
  'kn': 'ಕನ್ನಡ (Kannada)'
};

const WELCOME_MESSAGES = {
  'en': 'How are you feeling today?',
  'hi': 'आज आप कैसा महसूस कर रहे हैं?',
  'bn': 'আজ আপনি কেমন অনুভব করছেন?',
  'bho': 'आज रउआ कइसन लागत बा?',
  'kn': 'ಇಂದು ನೀವು ಹೇಗೆ ಅನಿಸುತ್ತಿದೆ?'
};

function App() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isConnected, setIsConnected] = useState(true);
  const [isListening, setIsListening] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [isNewsModalOpen, setIsNewsModalOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const fileInputRef = useRef(null);

  // Scroll to bottom when new messages are added
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check backend health on component mount
  useEffect(() => {
    checkBackendHealth();
    initializeVoiceRecognition();
  }, []);

  // Initialize voice recognition
  const initializeVoiceRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();

      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.maxAlternatives = 1;

      recognitionRef.current.onstart = () => {
        setIsListening(true);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputText(transcript);
        // Auto-send the transcribed message with voice flag
        setTimeout(() => sendMessage(transcript, null, true), 100);
      };

      recognitionRef.current.onerror = (event) => {
        setIsListening(false);
        setError(`Speech recognition error: ${event.error}`);
      };
    }
  };

  // Update speech recognition language when selectedLanguage changes
  useEffect(() => {
    if (recognitionRef.current) {
      const speechLanguageCodes = {
        'en': 'en-US',
        'hi': 'hi-IN',
        'bn': 'bn-IN',
        'bho': 'hi-IN', // Fallback to Hindi for Bhojpuri
        'kn': 'kn-IN'
      };
      recognitionRef.current.lang = speechLanguageCodes[selectedLanguage] || 'en-US';
    }
  }, [selectedLanguage]);

  const checkBackendHealth = async () => {
    try {
      const response = await fetch('/api/health');
      const data = await response.json();
      console.log('Backend health response:', data);
      setIsConnected(data.status === 'healthy');
    } catch (err) {
      setIsConnected(false);
      console.error('Backend health check failed:', err);
    }
  };

  const sendMessage = async (messageText = inputText, audioData = null, isVoiceInput = false) => {
    console.log('sendMessage called with:', { messageText, audioData, isVoiceInput, isConnected, isLoading });
    if (!messageText.trim() && !audioData) return;

    const userMessage = {
      id: Date.now(),
      message: messageText,
      language: selectedLanguage,
      timestamp: new Date(),
      is_user: true
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);
    setError(null);

    try {
      let response;

      if (audioData) {
        // Use audio endpoint for audio data
        response = await fetch('/api/chat/audio-base64', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            audio: audioData,
            language: selectedLanguage,
            user_id: 1
          })
        });
      } else {
        // Use text endpoint for text messages
        response = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: messageText,
            language: selectedLanguage,
            user_id: 1
          })
        });
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      const botMessage = {
        id: Date.now() + 1,
        message: data.reply,
        language: selectedLanguage,
        timestamp: new Date(),
        is_user: false,
        sources: data.sources || [],
        translation_unavailable: data.translation_unavailable || false
      };

      setMessages(prev => [...prev, botMessage]);

      // Auto-play TTS only for voice inputs (voice-to-voice)
      if (isVoiceInput && data.reply && 'speechSynthesis' in window) {
        speakText(data.reply, selectedLanguage);
      }
    } catch (err) {
      console.error('Chat error:', err);
      setError(err.message);

      // Add error message to chat
      const errorMessage = {
        id: Date.now() + 1,
        message: `Error: ${err.message}. Please check your connection and try again.`,
        language: selectedLanguage,
        timestamp: new Date(),
        is_user: false,
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputText, null, false); // Text-to-text, no voice response
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputText, null, false); // Text-to-text, no voice response
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  // Voice input handler
  const handleVoiceInput = () => {
    if (isListening) {
      // Stop listening
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    } else {
      // Start listening
      if (recognitionRef.current) {
        try {
          recognitionRef.current.start();
        } catch (error) {
          setError('Failed to start voice recognition');
        }
      } else {
        setError('Voice recognition not supported in this browser');
      }
    }
  };

  // Client-Side TTS using VoiceManager
  const speakText = async (text, language = selectedLanguage) => {
    try {
      if (!text) return;
      await voiceManager.speak(text, language);
    } catch (err) {
      console.error('TTS error:', err);
      // Fail silently or show toast, but valid client-side speech shouldn't fail often
    }
  };

  // Document upload handler
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type.startsWith('image/')) {
      handleImageUpload(event);
      return;
    }

    // Handle PDF/JSON upload
    uploadDocument(file);
  };

  const uploadDocument = async (file) => {
    setIsLoading(true);

    // Add optimistic message
    setMessages(prev => [...prev, {
      id: Date.now(),
      message: `Uploading ${file.name}...`,
      is_user: true,
      language: selectedLanguage,
      timestamp: new Date()
    }]);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', 1); // Mock user ID

    try {
      const response = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) throw new Error('Upload failed');

      const data = await response.json();

      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        message: `✅ Analyzed ${file.name}. I extracted the data. You can now ask questions about it!`,
        is_user: false,
        language: selectedLanguage,
        timestamp: new Date(),
        sources: [{ title: file.name, source: "User Upload" }]
      }]);

    } catch (error) {
      console.error('Upload error:', error);
      setError(`Failed to upload ${file.name}`);
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        message: `❌ Failed to process ${file.name}.`,
        is_user: false,
        isError: true,
        language: selectedLanguage,
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  // Image upload handler (existing logic wrapped or kept distinct)
  const handleImageUpload = (event) => {
    const file = event.target.files[0] || (event.target.files && event.target.files[0]);
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setSelectedImage({
          file: file,
          preview: e.target.result,
          name: file.name
        });
      };
      reader.readAsDataURL(file);
    } else {
      setError('Please select a valid image file');
    }
  };

  // Send image for analysis
  const sendImageForAnalysis = async () => {
    if (!selectedImage) return;

    const userMessage = {
      id: Date.now(),
      message: `Analyzing image: ${selectedImage.name}`,
      language: selectedLanguage,
      timestamp: new Date(),
      is_user: true,
      image: selectedImage.preview
    };

    setMessages(prev => [...prev, userMessage]);
    setSelectedImage(null);
    setIsLoading(true);
    setError(null);

    try {
      // Convert image to base64 for sending to backend
      const base64Image = selectedImage.preview.split(',')[1];

      const response = await fetch('/api/chat/image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image: base64Image,
          filename: selectedImage.name,
          message: "Please analyze this medical image and provide insights.",
          language: selectedLanguage,
          user_id: 1
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      const botMessage = {
        id: Date.now() + 1,
        message: data.reply,
        language: selectedLanguage,
        timestamp: new Date(),
        is_user: false,
        sources: data.sources || [],
        translation_unavailable: data.translation_unavailable || false
      };

      setMessages(prev => [...prev, botMessage]);

    } catch (err) {
      console.error('Image analysis error:', err);
      setError(err.message);

      const errorMessage = {
        id: Date.now() + 1,
        message: `Error analyzing image: ${err.message}. Please try again.`,
        language: selectedLanguage,
        timestamp: new Date(),
        is_user: false,
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Clear selected image
  const clearSelectedImage = () => {
    setSelectedImage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };



  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <div className="app-title">Dhanvantri AI</div>
          <div className="language-selector">
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="language-select"
            >
              {Object.entries(SUPPORTED_LANGUAGES).map(([code, name]) => (
                <option key={code} value={code}>{name}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="header-right">
          <button
            onClick={() => setIsNewsModalOpen(true)}
            className="news-button"
            title="View Health News"
          >
            📰 News
          </button>

          <div className="status-indicator">
            <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
            <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>

          <button
            onClick={checkBackendHealth}
            className="clear-button"
            title="Refresh connection"
          >
            🔄
          </button>
          <button
            onClick={clearChat}
            className="clear-button"
            disabled={messages.length === 0}
          >
            Clear
          </button>
        </div>
      </header>

      <main className="chat-container">
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <div className="dhanvantri-logo">
                <img src="/dhanvantri-logo.svg" alt="Dhanvantri" className="logo-image" />
              </div>
              <div className="app-name">Dhanvantri AI</div>
              <div className="welcome-title">{WELCOME_MESSAGES[selectedLanguage] || WELCOME_MESSAGES['en']}</div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.is_user ? 'user-message' : 'bot-message'} ${message.isError ? 'error-message' : ''}`}
            >
              <div className="message-content">
                <div className="message-avatar">
                  {message.is_user ? '👤' : '🏥'}
                </div>
                <div className="message-body">
                  <div className="message-text">
                    {message.message}
                  </div>

                  {!message.is_user && (
                    <div className="message-actions">
                      <button
                        className="tts-button"
                        onClick={() => speakText(message.message, message.language)}
                        disabled={isLoading}
                        title="Listen to this message"
                      >
                        {isLoading ? '⏳' : '🔊'}
                      </button>
                    </div>
                  )}

                  {message.image && (
                    <div className="message-image">
                      <img
                        src={message.image}
                        alt="Uploaded medical image"
                        className="uploaded-image"
                      />
                    </div>
                  )}

                  {message.translation_unavailable && (
                    <div className="translation-warning">
                      ⚠️ Translation unavailable - response provided in English
                    </div>
                  )}

                  {message.sources && message.sources.length > 0 && (
                    <div className="message-sources">
                      <strong>Sources:</strong>
                      {message.sources.map((source, index) => (
                        <span key={index} className="source-tag">
                          {source.title} ({source.source})
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="message-meta">
                    <span>{formatTimestamp(message.timestamp)}</span>
                    <span>{SUPPORTED_LANGUAGES[message.language] || message.language}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="message bot-message loading-message">
              <div className="message-content">
                <div className="message-avatar">🏥</div>
                <div className="message-body">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </main>

      <footer className="chat-input-container">
        {error && (
          <div className="error-banner">
            <span>⚠️ {error}</span>
            <button onClick={() => setError(null)} className="error-close">×</button>
          </div>
        )}

        {selectedImage && (
          <div className="image-preview">
            <div className="image-preview-content">
              <img src={selectedImage.preview} alt="Selected image" className="preview-image" />
              <div className="image-preview-info">
                <span className="image-name">{selectedImage.name}</span>
                <div className="image-preview-actions">
                  <button
                    onClick={sendImageForAnalysis}
                    className="analyze-button"
                    disabled={isLoading || !isConnected}
                  >
                    {isLoading ? '⏳ Analyzing...' : '🔍 Analyze Image'}
                  </button>
                  <button
                    onClick={clearSelectedImage}
                    className="clear-image-button"
                  >
                    ✕
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="chat-form">
          <div className="input-group">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept="image/*,application/pdf,application/json"
              style={{ display: 'none' }}
            />
            <button
              type="button"
              className="upload-button"
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading || !isConnected}
              title="Upload medical image for analysis"
            >
              +
            </button>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask anything..."
              className="chat-input"
              rows="1"
              disabled={isLoading || !isConnected}
            />
            <div className="input-actions">
              <button
                type="button"
                className={`voice-input-button ${isListening ? 'active' : ''}`}
                onClick={handleVoiceInput}
                disabled={isLoading || !isConnected}
                title={isListening ? 'Stop listening (Voice-to-Voice)' : 'Voice-to-Voice chat'}
              >
                {isListening ? '🔴' : '🎤'}
              </button>
              <button
                type="submit"
                className="send-button"
                disabled={!inputText.trim() || isLoading || !isConnected}
                title="Send text message (Text-to-Text)"
              >
                {isLoading ? '⏳' : '↑'}
              </button>
            </div>
          </div>
        </form>


      </footer>

      <NewsModal
        isOpen={isNewsModalOpen}
        onClose={() => setIsNewsModalOpen(false)}
      />
    </div>
  );
}

export default App;