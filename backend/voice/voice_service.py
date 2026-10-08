from typing import Dict, Any, Optional
from voice.voice_config import voice_config
from voice.voice_provider import WebSpeechVoiceProvider, IVoiceProvider

class VoiceService:
    def __init__(self):
        self._provider: IVoiceProvider = WebSpeechVoiceProvider()
        
    def set_provider(self, provider: IVoiceProvider):
        self._provider = provider

    async def speak(self, text: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not voice_config.enabled:
            return {"status": "disabled", "message": "Voice output is currently disabled."}
            
        opts = {
            "rate": voice_config.rate,
            "pitch": voice_config.pitch,
            "volume": voice_config.volume,
            "voice_name": voice_config.voice_name,
            **(options or {})
        }
        return await self._provider.speak(text, opts)

    def get_status(self) -> Dict[str, Any]:
        provider_status = self._provider.get_status()
        return {
            "enabled": voice_config.enabled,
            "auto_speak": voice_config.auto_speak,
            "rate": voice_config.rate,
            "pitch": voice_config.pitch,
            "volume": voice_config.volume,
            **provider_status
        }

voice_service = VoiceService()
