from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("mikasa.voice")

class IVoiceProvider(ABC):
    @abstractmethod
    async def speak(self, text: str, voice_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Synthesize speech or return speech instructions."""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Return provider status."""
        pass

class WebSpeechVoiceProvider(IVoiceProvider):
    """
    Standard voice provider delegating synthesis to client-side Web Speech API
    configured with authorized voice parameters.
    """
    def __init__(self):
        self.name = "MIKASA Authorized Voice Engine"

    async def speak(self, text: str, voice_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = voice_params or {}
        return {
            "status": "ready",
            "type": "client_synthesis",
            "text": text,
            "voice_name": params.get("voice_name", "MIKASA Voice"),
            "rate": params.get("rate", 1.0),
            "pitch": params.get("pitch", 1.0),
            "volume": params.get("volume", 1.0)
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "available": True,
            "provider": "web_speech",
            "description": "Authorized Voice Synthesis Ready"
        }
