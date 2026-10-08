from typing import AsyncIterator, List, Dict, Any, Optional
from core.config import config
from core.mikasa_personality import build_system_prompt
from ollama_handler import stream_chat_with_config, check_inference_health

class MikasaBrain:
    """Stable MIKASA brain interface. The inference runtime is an internal implementation detail."""
    def __init__(self):
        self.name = "MIKASA"

    async def stream(
        self,
        messages: List[Dict[str, str]],
        memory_context: Optional[str] = None,
        response_style: str = "balanced"
    ) -> AsyncIterator[str]:
        sys_prompt = build_system_prompt(memory_context=memory_context, response_style=response_style)
        async for chunk in stream_chat_with_config(
            messages=messages,
            base_url=config.ollama_url,
            model=config.model,
            system_prompt=sys_prompt
        ):
            yield chunk

    async def generate(
        self,
        messages: List[Dict[str, str]],
        memory_context: Optional[str] = None,
        response_style: str = "balanced"
    ) -> str:
        collected = []
        async for chunk in self.stream(messages, memory_context=memory_context, response_style=response_style):
            collected.append(chunk)
        return "".join(collected)

    async def check_status(self) -> Dict[str, Any]:
        health = await check_inference_health(config.ollama_url, config.model)
        return {
            "name": self.name,
            "mode": "local",
            "brain_online": health["online"],
            "brain_ready": health["model_ready"]
        }

brain = MikasaBrain()
