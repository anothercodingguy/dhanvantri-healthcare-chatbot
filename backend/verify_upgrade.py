import asyncio
import os
import sys

# Adjust path to include the current directory (backend)
sys.path.append(os.getcwd())

from services.groq_client import groq_client
from services.edge_tts_service import edge_tts_service
from config import settings

async def verify_upgrade():
    print("🧪 Verifying High-End TTS/STT Upgrade...")
    
    if not settings.groq_api_key:
        print("❌ Error: GROQ_API_KEY is missing.")
        return

    # 1. Test Edge TTS (Neural Voice)
    print("\n1. Testing Edge TTS (Neural)...")
    try:
        # English
        print("   Generating English Audio (AriaNeural)...")
        audio_en = await edge_tts_service.generate_speech_async("Hello, this is a high quality neural voice.", "en")
        if audio_en:
             print(f"   ✅ English Audio Generated ({len(audio_en)} bytes)")
        else:
             print("   ❌ English Audio Failed")

        # Hindi
        print("   Generating Hindi Audio (SwaraNeural)...")
        audio_hi = await edge_tts_service.generate_speech_async("नमस्ते, यह एक उच्च गुणवत्ता वाली आवाज है।", "hi")
        if audio_hi:
             print(f"   ✅ Hindi Audio Generated ({len(audio_hi)} bytes)")
             
    except Exception as e:
        print(f"   ❌ TTS Verification Failed: {e}")

    # 2. Test Groq STT (Quick Check)
    print("\n2. Testing Groq STT Connection...")
    try:
        # We don't have a file to test easily without uploading, 
        # but we can check if client initializes without error.
        if groq_client.client:
            print("   ✅ Groq Client Initialized")
    except Exception as e:
        print(f"   ❌ Groq Client Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_upgrade())
