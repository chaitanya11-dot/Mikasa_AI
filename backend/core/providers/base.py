from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Dict, Any, Optional

class BaseIntelligenceProvider(ABC):
    """
    Abstract base class for all MIKASA intelligence providers.
    Both Local and Online provider implementations inherit from this.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the provider (e.g., 'local_ollama', 'online_openai')."""
        pass

    @property
    @abstractmethod
    def provider_type(self) -> str:
        """Provider category: 'local' or 'online'."""
        pass

    @abstractmethod
    async def stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """Stream token chunks from this provider."""
        pass

    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> str:
        """Collect all streamed chunks into a single response string."""
        tokens = []
        async for chunk in self.stream(
            messages=messages,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        ):
            tokens.append(chunk)
        return "".join(tokens)

    @abstractmethod
    async def check_status(self) -> Dict[str, Any]:
        """
        Check health and readiness of this intelligence provider.
        Returns a dict containing 'online' (bool), 'ready' (bool), and diagnostic details.
        """
        pass
