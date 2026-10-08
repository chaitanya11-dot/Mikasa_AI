import os
from dataclasses import dataclass

@dataclass
class VoiceConfig:
    enabled: bool = True
    auto_speak: bool = False
    voice_name: str = os.getenv("MIKASA_VOICE_NAME", "MIKASA Authorized Voice")
    rate: float = float(os.getenv("MIKASA_VOICE_RATE", "1.0"))
    pitch: float = float(os.getenv("MIKASA_VOICE_PITCH", "1.0"))
    volume: float = float(os.getenv("MIKASA_VOICE_VOLUME", "1.0"))
    provider: str = os.getenv("MIKASA_VOICE_PROVIDER", "web_speech")

voice_config = VoiceConfig()
