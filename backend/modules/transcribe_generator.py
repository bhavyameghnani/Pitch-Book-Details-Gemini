import os
import google.generativeai as genai
import base64
from dotenv import load_dotenv

load_dotenv()

def configure_gemini():
    """Configures the Gemini API with the key from environment variables."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found. Please set it in a .env file.")
    genai.configure(api_key=api_key)

# Initialize Gemini at startup
configure_gemini()

def transcribe_audio_with_gemini(audio_path: str) -> str:
    """Transcribe audio file to text using Gemini multimodal."""
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = "You are an expert transcriptionist. Transcribe the following audio file to text. Only return the transcript, no extra commentary."

    # Read audio as Base64
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    # Wrap properly for Gemini
    audio_part = {
        "mime_type": "audio/mp3" if audio_path.endswith(".mp3") else "audio/wav",
        "data": audio_b64
    }

    # Pass as structured input
    response = model.generate_content([prompt, audio_part])
    return response.text.strip()