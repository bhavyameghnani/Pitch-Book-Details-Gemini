# main.py
import os
import re
import io
import json
import time
import functools
import fitz  # PyMuPDF
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from tempfile import NamedTemporaryFile
import base64
from modules.transcript_analysis import analyze_transcript_with_ai
from modules.pitch_deck_analysis import process_pitch_deck
from modules.transcribe_generator import transcribe_audio_with_gemini


# ===============================
# Environment Setup
# ===============================
load_dotenv()

def configure_gemini():
    """Configures the Gemini API with the key from environment variables."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found. Please set it in a .env file.")
    genai.configure(api_key=api_key)

# Initialize Gemini at startup
configure_gemini()

# ===============================
# Pydantic Base Model
# ===============================
class TranscriptRequest(BaseModel):
    transcript: str


# ===============================
# FastAPI App
# ===============================
app = FastAPI(
    title="Startup Pitch Analyzer API",
    description="Analyze transcripts and pitch decks using Google's Gemini",
    version="2.0.0"
)

# after creating `app = FastAPI(...)`
origins = [
    "http://localhost:3000",  # Next dev server
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to the Startup Pitch Analyzer API "}

# --- Transcript Endpoints ---
@app.post("/analyze-text/")
async def analyze_text(request: TranscriptRequest):
    if not request.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty.")
    insights = analyze_transcript_with_ai(request.transcript)
    return JSONResponse(content=insights)

@app.post("/analyze-file/")
async def analyze_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported.")
    content = (await file.read()).decode("utf-8")
    insights = analyze_transcript_with_ai(content)
    return JSONResponse(content=insights)

# --- Audio Transcript Endpoint ---
@app.post("/analyze-audio/")
async def analyze_audio(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".wav", ".mp3", ".m4a", ".ogg")):
        raise HTTPException(status_code=400, detail="Only audio files (.wav, .mp3, .m4a, .ogg) are supported.")
    
    # Save to temp file
    with NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[-1]) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    
    try:
        transcript = transcribe_audio_with_gemini(tmp_path)
        if not transcript or not transcript.strip():
            raise HTTPException(status_code=500, detail="Transcription failed or returned empty text.")
        
        insights = analyze_transcript_with_ai(transcript)
        return JSONResponse(content={"transcript": transcript, "analysis": insights})
    finally:
        os.remove(tmp_path)


@app.post("/analyze-pitch-deck/")
async def analyze_pitch_deck(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only .pdf files are supported.")
    
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    
    try:
        result = process_pitch_deck(temp_path)
        return JSONResponse(content=result)
    finally:
        os.remove(temp_path)
