import logging
from typing import AsyncIterator, List, Dict, Any, Optional
from core.providers.base import BaseIntelligenceProvider
from core.config import config
from ollama_handler import stream_chat_with_config, check_inference_health

logger = logging.getLogger("mikasa.provider.local")

class LocalMikasaProvider(BaseIntelligenceProvider):
    """
    Local MIKASA intelligence provider.
    Runs local LLM inference on-device (via Ollama / local runtime).
    """

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self._base_url = base_url or config.ollama_url
        self._model = model or config.model

    @property
    def name(self) -> str:
        return "local_mikasa"

    @property
    def provider_type(self) -> str:
        return "local"

    @property
    def model(self) -> str:
        return self._model

    @property
    def base_url(self) -> str:
        return self._base_url

    async def stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """Stream responses from the local model."""
        base_url = kwargs.get("base_url", self._base_url)
        model = kwargs.get("model", self._model)
        
        async for chunk in stream_chat_with_config(
            messages=messages,
            base_url=base_url,
            model=model,
            system_prompt=system_prompt
        ):
            yield chunk

    async def check_status(self) -> Dict[str, Any]:
        """Query local runtime health and verify if local model is loaded/ready."""
        health = await check_inference_health(self._base_url, self._model)
        return {
            "provider": self.name,
            "type": self.provider_type,
            "online": health.get("online", False),
            "ready": health.get("model_ready", False),
            "model": self._model,
            "base_url": self._base_url,
            "details": health
        }
