import os
import sys

# Set mock-model env var BEFORE importing config
os.environ["MODEL_NAME"] = "mock-model"

sys.path.append(os.getcwd())
try:
    from config import settings
    print(f"ENV MODEL_NAME: {os.environ.get('MODEL_NAME')}")
    print(f"SETTINGS MODEL_NAME: {settings.model_name}")
    
    if settings.model_name == "llama-3.3-70b-versatile":
        print("✅ SUCCESS: Config correctly overrode mock-model")
    else:
        print(f"❌ FAILURE: Config stayed as {settings.model_name}")
except Exception as e:
    print(f"❌ FAILURE: {e}")
