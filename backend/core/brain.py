from typing import AsyncIterator, List, Dict, Any, Optional
from core.config import config
from core.router.intelligence_router import router, IntelligenceRouter

class MikasaBrain:
    """
    MIKASA Brain facade in V2.1.
    Delegates all cognitive processing to the Intelligence Router, seamlessly
    coordinating between Local MIKASA and Online MIKASA provider engines.
    """
    def __init__(self, intelligence_router: Optional[IntelligenceRouter] = None):
        self.name = "MIKASA"
        self.router = intelligence_router or router

    async def stream(
        self,
        messages: List[Dict[str, str]],
        memory_context: Optional[str] = None,
        response_style: str = "balanced",
        routing_mode: Optional[str] = None
    ) -> AsyncIterator[str]:
        """Stream generated responses via the Intelligence Router."""
        async for chunk in self.router.stream(
            messages=messages,
            memory_context=memory_context,
            response_style=response_style,
            routing_mode=routing_mode
        ):
            yield chunk

    async def generate(
        self,
        messages: List[Dict[str, str]],
        memory_context: Optional[str] = None,
        response_style: str = "balanced",
        routing_mode: Optional[str] = None
    ) -> str:
        """Generate full response via the Intelligence Router."""
        return await self.router.generate(
            messages=messages,
            memory_context=memory_context,
            response_style=response_style,
            routing_mode=routing_mode
        )

    async def check_status(self) -> Dict[str, Any]:
        """Check status of Brain and underlying router/providers."""
        router_status = await self.router.check_status()
        return {
            "name": self.name,
            "version": config.version,
            "mode": router_status.get("routing_mode", "local_only"),
            "brain_online": router_status.get("brain_online", False),
            "brain_ready": router_status.get("brain_ready", False),
            "router": router_status
        }

brain = MikasaBrain()
