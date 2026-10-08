from fastapi import APIRouter
from voice.voice_service import voice_service
from models.chat_model import VoiceSpeakRequest

router = APIRouter(prefix="/api/voice", tags=["voice"])

@router.get("/status")
async def voice_status():
    return voice_service.get_status()

@router.post("/speak")
async def speak_text(req: VoiceSpeakRequest):
    return await voice_service.speak(req.text, req.options)

@router.post("/transcribe")
async def transcribe_audio():
    # Modular STT bridge endpoint
    return {"status": "ok", "provider": "web_speech_or_native", "message": "Ready for voice input"}
