import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class MikasaConfig:
    name: str = "MIKASA"
    version: str = os.getenv("MIKASA_VERSION", "2.1.0")
    host: str = os.getenv("MIKASA_HOST", "127.0.0.1")
    port: int = int(os.getenv("MIKASA_PORT", "8000"))
    ollama_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    model: str = os.getenv("MIKASA_MODEL", os.getenv("OLLAMA_MODEL", "mikasa:latest"))
    routing_mode: str = os.getenv("MIKASA_ROUTING_MODE", "local_only")
    online_api_key: str = os.getenv("MIKASA_ONLINE_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    online_base_url: str = os.getenv("MIKASA_ONLINE_BASE_URL", "https://api.openai.com/v1")
    online_model: str = os.getenv("MIKASA_ONLINE_MODEL", "gpt-4o-mini")
    router_fallback: bool = os.getenv("MIKASA_ROUTER_FALLBACK", "true").lower() in ("true", "1", "yes")
    data_dir: str = os.getenv(
        "MIKASA_DATA_DIR",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    )

config = MikasaConfig()