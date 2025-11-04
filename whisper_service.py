#!/usr/bin/env python3
"""
Simple Whisper transcription service
Provides a REST API endpoint for audio transcription using OpenAI Whisper
"""

from flask import Flask, request, jsonify
import whisper
import base64
import io
import tempfile
import os

app = Flask(__name__)

# Enable CORS if available (optional)
try:
    from flask_cors import CORS
    CORS(app)
    print("CORS enabled")
except ImportError:
    print("flask-cors not installed - CORS not enabled")

# Load Whisper model (using 'base' for balance of speed and accuracy)
print("Loading Whisper model...")
model = whisper.load_model("base")
print("Whisper model loaded successfully")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "whisper-transcription"})

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """
    Transcribe audio data sent as base64 encoded string
    Expected JSON payload: {"audio": "base64_encoded_audio_data"}
    """
    try:
        # Get audio data from request
        if not request.json or 'audio' not in request.json:
            return jsonify({"error": "Missing 'audio' field in request"}), 400
        
        audio_data = request.json['audio']
        
        # Decode base64 audio data
        try:
            audio_bytes = base64.b64decode(audio_data)
        except Exception as e:
            return jsonify({"error": f"Invalid base64 audio data: {str(e)}"}), 400
        
        # Create temporary file for audio processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        
        try:
            # Transcribe audio using Whisper
            result = model.transcribe(temp_file_path)
            transcribed_text = result["text"].strip()
            
            return jsonify({
                "text": transcribed_text,
                "language": result.get("language", "unknown"),
                "status": "success"
            })
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500

@app.route('/models', methods=['GET'])
def list_models():
    """List available Whisper models"""
    available_models = [
        "tiny", "base", "small", "medium", "large"
    ]
    return jsonify({
        "available_models": available_models,
        "current_model": "base"
    })

if __name__ == '__main__':
    print("Starting Whisper transcription service...")
    print("Service will be available at http://localhost:5001")
    print("Endpoints:")
    print("  GET  /health - Health check")
    print("  POST /transcribe - Transcribe audio")
    print("  GET  /models - List available models")
    
    app.run(host='0.0.0.0', port=5001, debug=True)