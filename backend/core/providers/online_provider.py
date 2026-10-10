import httpx
import json
import logging
from typing import AsyncIterator, List, Dict, Any, Optional
from core.providers.base import BaseIntelligenceProvider
from core.config import config

logger = logging.getLogger("mikasa.provider.online")

class OnlineProviderError(Exception):
    """Custom exception for online provider errors."""
    pass

class OnlineMikasaProvider(BaseIntelligenceProvider):
    """
    Online MIKASA intelligence provider abstraction.
    Connects to external high-performance LLM endpoints (OpenAI-compatible APIs,
    OpenRouter, Anthropic adapters, Groq, Together, DeepSeek, etc.).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0
    ):
        self._api_key = api_key or config.online_api_key
        self._base_url = (base_url or config.online_base_url).rstrip("/")
        self._model = model or config.online_model
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "online_mikasa"

    @property
    def provider_type(self) -> str:
        return "online"

    @property
    def model(self) -> str:
        return self._model

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def is_configured(self) -> bool:
        """Check if an API key or custom endpoint is configured."""
        return bool(self._api_key and self._api_key.strip())

    async def stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """Stream chat completions from online provider."""
        api_key = kwargs.get("api_key", self._api_key)
        base_url = kwargs.get("base_url", self._base_url).rstrip("/")
        model = kwargs.get("model", self._model)

        if not api_key:
            logger.warning("Online provider attempted without API key configured.")
            raise OnlineProviderError("Online provider API key is not configured. Please add an API key in settings.")

        url = f"{base_url}/chat/completions" if not base_url.endswith("/chat/completions") else base_url

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Build message history with system prompt
        max_history = kwargs.get("max_history_messages", 20)
        recent_msgs = messages[-max_history:] if len(messages) > max_history else messages

        formatted = [{"role": "system", "content": system_prompt}] + [
            {"role": m.get("role", "user"), "content": m.get("content", "")}
            for m in recent_msgs
            if m.get("content")
        ]

        payload: Dict[str, Any] = {
            "model": model,
            "messages": formatted,
            "stream": True,
            "temperature": temperature
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        timeout = httpx.Timeout(self._timeout, connect=10.0)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    if response.status_code in (401, 403):
                        logger.error(f"Online provider authorization failed ({response.status_code}).")
                        raise OnlineProviderError(f"Online provider authorization failed (HTTP {response.status_code}). Please verify your API key.")
                    elif response.status_code == 429:
                        logger.warning("Online provider rate limit / quota exceeded (429).")
                        raise OnlineProviderError("Online provider rate limit or quota exceeded (HTTP 429).")
                    elif response.status_code != 200:
                        error_text = await response.aread()
                        decoded_err = error_text.decode('utf-8', errors='ignore')
                        logger.error(f"Online provider returned HTTP {response.status_code}: {decoded_err}")
                        raise OnlineProviderError(f"Online provider returned HTTP status {response.status_code}: {decoded_err[:200]}")

                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        line = line.strip()
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                parsed = json.loads(data_str)
                                choices = parsed.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue

        except (httpx.ConnectError, httpx.NetworkError) as exc:
            logger.warning(f"Online provider connection failed: {exc}")
            raise OnlineProviderError(f"Online provider connection failed: {exc}")
        except httpx.TimeoutException as exc:
            logger.warning("Online provider request timed out.")
            raise OnlineProviderError("Online provider request timed out.")
        except OnlineProviderError:
            raise
        except Exception as exc:
            logger.exception(f"Unexpected online provider stream error: {exc}")
            raise OnlineProviderError(f"Unexpected online provider error: {exc}")

    async def check_status(self) -> Dict[str, Any]:
        """Check online provider configuration and reachability."""
        if not self.is_configured:
            return {
                "provider": self.name,
                "type": self.provider_type,
                "online": False,
                "ready": False,
                "configured": False,
                "model": self._model,
                "base_url": self._base_url,
                "message": "API key not configured"
            }

        # Validate connectivity if key is present
        try:
            url = f"{self._base_url}/models"
            headers = {"Authorization": f"Bearer {self._api_key}"}
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(url, headers=headers)
                online = resp.status_code == 200
                return {
                    "provider": self.name,
                    "type": self.provider_type,
                    "online": online,
                    "ready": online,
                    "configured": True,
                    "model": self._model,
                    "base_url": self._base_url,
                    "status_code": resp.status_code
                }
        except Exception as exc:
            logger.debug(f"Online provider reachability check: {exc}")
            return {
                "provider": self.name,
                "type": self.provider_type,
                "online": True,  # Key is present, network might be intermittent
                "ready": True,
                "configured": True,
                "model": self._model,
                "base_url": self._base_url,
                "note": "Configured (live ping skipped or timed out)"
            }
