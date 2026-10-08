import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class MikasaConfig:
    name: str = "MIKASA"
    version: str = os.getenv("MIKASA_VERSION", "1.0.0")
    host: str = os.getenv("MIKASA_HOST", "127.0.0.1")
    port: int = int(os.getenv("MIKASA_PORT", "8000"))
    ollama_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    model: str = os.getenv("MIKASA_MODEL", os.getenv("OLLAMA_MODEL", "mikasa:latest"))
    data_dir: str = os.getenv(
        "MIKASA_DATA_DIR",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    )

config = MikasaConfig()