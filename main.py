from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import OpenAI
import uvicorn
from pathlib import Path
import tempfile
from typing import Optional, List, Dict
from dotenv import load_dotenv
import os
import base64

# Load environment variables
load_dotenv()

app = FastAPI()

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Simple in-memory chat history
chat_history: List[Dict[str, str]] = []


def transcribe_audio(audio_path: str) -> Optional[str]:
    """Convert speech to text using OpenAI's Whisper"""
    try:
        with open(audio_path, "rb") as audio:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                response_format="text"
            )
        return transcript
    except Exception as e:
        print(f"Transcription error: {e}")
        return None


def process_with_llm(text: str) -> Optional[str]:
    """Process text with LLM using conversation history"""
    try:
        # Build messages with history
        messages = [
            {"role": "system", "content": "You are a helpful voice assistant. Keep responses concise and natural."}
        ] + chat_history + [{"role": "user", "content": text}]

        # Get response from GPT
        chat_completion = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages
        )

        response = chat_completion.choices[0].message.content

        # Update history
        chat_history.append({"role": "user", "content": text})
        chat_history.append({"role": "assistant", "content": response})

        # Keep only last 10 exchanges (20 messages) to manage context length
        while len(chat_history) > 20:
            chat_history.pop(0)

        return response
    except Exception as e:
        print(f"LLM processing error: {e}")
        return None


def convert_to_speech(text: str) -> Optional[bytes]:
    """Convert text to speech using OpenAI's TTS"""
    try:
        speech_response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        return speech_response.content
    except Exception as e:
        print(f"Text-to-speech error: {e}")
        return None


@app.post("/process-voice")
async def process_voice(audio_file: UploadFile = File(...)):
    try:
        # Save uploaded audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            content = await audio_file.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name

        # Step 1: Speech to Text
        transcript = transcribe_audio(temp_audio_path)
        if not transcript:
            return JSONResponse(content={"error": "Transcription failed"}, status_code=500)

        # Step 2: Process with LLM
        response_text = process_with_llm(transcript)
        if not response_text:
            return JSONResponse(content={"error": "LLM processing failed"}, status_code=500)

        # Step 3: Text to Speech
        audio_content = convert_to_speech(response_text)
        if not audio_content:
            return JSONResponse(content={"error": "Text-to-speech conversion failed"}, status_code=500)

        # Cleanup temporary audio file
        Path(temp_audio_path).unlink()

        # Encode audio content as base64
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')

        return JSONResponse(content={
            "transcript": transcript,
            "response_text": response_text,
            "audio": audio_base64,
            "history": chat_history
        })

    except Exception as e:
        print(f"Error in process_voice: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
