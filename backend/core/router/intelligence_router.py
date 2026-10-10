import logging
from enum import Enum
from typing import AsyncIterator, List, Dict, Any, Optional
from dataclasses import dataclass

from core.config import config
from core.mikasa_personality import build_system_prompt
from core.providers.base import BaseIntelligenceProvider
from core.providers.local_provider import LocalMikasaProvider
from core.providers.online_provider import OnlineMikasaProvider

logger = logging.getLogger("mikasa.router")

class RoutingMode(str, Enum):
    LOCAL_ONLY = "local_only"
    LOCAL_FIRST = "local_first"
    ONLINE_FIRST = "online_first"
    ONLINE_ONLY = "online_only"
    AUTO = "auto"

    @classmethod
    def normalize(cls, mode_str: Optional[str]) -> "RoutingMode":
        if not mode_str:
            return cls.LOCAL_ONLY
        normalized = mode_str.lower().strip().replace("-", "_")
        if normalized in ("local", "local_only"):
            return cls.LOCAL_ONLY
        elif normalized in ("local_first", "localfirst"):
            return cls.LOCAL_FIRST
        elif normalized in ("online", "online_only"):
            return cls.ONLINE_ONLY
        elif normalized in ("online_first", "onlinefirst"):
            return cls.ONLINE_FIRST
        elif normalized in ("auto", "intelligent", "smart"):
            return cls.AUTO
        return cls.LOCAL_ONLY

@dataclass
class RoutingDecision:
    selected_engine: str  # "local" or "online"
    mode: RoutingMode
    reason: str
    fallback_available: bool
    fallback_engine: Optional[str] = None

class IntelligenceRouter:
    """
    MIKASA Intelligence Router.
    Intelligently routes inference requests between Local MIKASA and Online MIKASA providers,
    supporting rule-based, intent-based, and failover routing strategies.
    """

    def __init__(
        self,
        local_provider: Optional[BaseIntelligenceProvider] = None,
        online_provider: Optional[BaseIntelligenceProvider] = None,
        default_mode: Optional[RoutingMode] = None
    ):
        self.local_provider = local_provider or LocalMikasaProvider()
        self.online_provider = online_provider or OnlineMikasaProvider()
        self.default_mode = default_mode or RoutingMode.normalize(config.routing_mode)
        logger.info(f"Intelligence Router initialized. Default mode: {self.default_mode.value}")

    def get_provider(self, engine_type: str) -> BaseIntelligenceProvider:
        if engine_type == "online":
            return self.online_provider
        return self.local_provider

    async def evaluate_route(
        self,
        messages: List[Dict[str, str]],
        routing_mode: Optional[str] = None
    ) -> RoutingDecision:
        """
        Evaluate and decide which intelligence provider should fulfill the request.
        """
        mode = RoutingMode.normalize(routing_mode) if routing_mode else self.default_mode
        user_prompt = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                user_prompt = m.get("content", "")
                break

        # Check online provider availability
        online_configured = isinstance(self.online_provider, OnlineMikasaProvider) and self.online_provider.is_configured

        # 1. Strict LOCAL_ONLY
        if mode == RoutingMode.LOCAL_ONLY:
            return RoutingDecision(
                selected_engine="local",
                mode=mode,
                reason="Explicit Local-Only policy (Sovereign local privacy)",
                fallback_available=False
            )

        # 2. Strict ONLINE_ONLY
        if mode == RoutingMode.ONLINE_ONLY:
            return RoutingDecision(
                selected_engine="online",
                mode=mode,
                reason="Explicit Online-Only policy",
                fallback_available=False
            )

        # 3. LOCAL_FIRST
        if mode == RoutingMode.LOCAL_FIRST:
            return RoutingDecision(
                selected_engine="local",
                mode=mode,
                reason="Local-First policy: prioritize local compute with online failover",
                fallback_available=online_configured,
                fallback_engine="online" if online_configured else None
            )

        # 4. ONLINE_FIRST
        if mode == RoutingMode.ONLINE_FIRST:
            selected = "online" if online_configured else "local"
            return RoutingDecision(
                selected_engine=selected,
                mode=mode,
                reason="Online-First policy" if online_configured else "Online not configured, falling back to local",
                fallback_available=True if selected == "online" else False,
                fallback_engine="local" if selected == "online" else None
            )

        # 5. AUTO / SMART ROUTING
        if mode == RoutingMode.AUTO:
            if not online_configured:
                return RoutingDecision(
                    selected_engine="local",
                    mode=mode,
                    reason="Auto routing: Online provider not configured, routing to local",
                    fallback_available=False
                )

            # Heuristic 1: Local engine health check
            local_status = await self.local_provider.check_status()
            if not local_status.get("online"):
                return RoutingDecision(
                    selected_engine="online",
                    mode=mode,
                    reason="Auto failover: Local inference is offline, routing to Online MIKASA",
                    fallback_available=False
                )

            # Heuristic 2: Long prompt / extended context (> 3000 chars)
            if len(user_prompt) > 3000:
                return RoutingDecision(
                    selected_engine="online",
                    mode=mode,
                    reason="Auto routing: Extended context length suitable for high-capacity online engine",
                    fallback_available=True,
                    fallback_engine="local"
                )

            # Heuristic 3: Complex coding / architecture / deep reasoning triggers
            complex_keywords = ["architecture design", "refactor whole project", "benchmark analysis", "complex algorithm"]
            lower_prompt = user_prompt.lower()
            if any(kw in lower_prompt for kw in complex_keywords):
                return RoutingDecision(
                    selected_engine="online",
                    mode=mode,
                    reason="Auto routing: Advanced reasoning / architectural workload detected",
                    fallback_available=True,
                    fallback_engine="local"
                )

            # Default to local for speed, privacy, and zero API cost
            return RoutingDecision(
                selected_engine="local",
                mode=mode,
                reason="Auto routing: Standard query dispatched to local MIKASA model",
                fallback_available=online_configured,
                fallback_engine="online" if online_configured else None
            )

        # Fallback default
        return RoutingDecision(
            selected_engine="local",
            mode=RoutingMode.LOCAL_ONLY,
            reason="Default local fallback",
            fallback_available=False
        )

    async def stream(
        self,
        messages: List[Dict[str, str]],
        memory_context: Optional[str] = None,
        response_style: str = "balanced",
        routing_mode: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """
        Stream response through the Intelligence Router with automatic failover.
        """
        sys_prompt = build_system_prompt(memory_context=memory_context, response_style=response_style)
        decision = await self.evaluate_route(messages, routing_mode=routing_mode)
        
        logger.info(f"Intelligence Router Decision: Engine={decision.selected_engine}, Mode={decision.mode.value}, Reason={decision.reason}")

        primary_provider = self.get_provider(decision.selected_engine)
        stream_succeeded = False
        chunks_yielded = 0

        try:
            async for chunk in primary_provider.stream(
                messages=messages,
                system_prompt=sys_prompt,
                **kwargs
            ):
                chunks_yielded += 1
                stream_succeeded = True
                yield chunk
        except Exception as primary_exc:
            logger.warning(f"Primary provider '{primary_provider.name}' stream failed: {primary_exc}")

        # Check if failover is required and possible
        if not stream_succeeded and decision.fallback_available and decision.fallback_engine:
            fallback_provider = self.get_provider(decision.fallback_engine)
            logger.info(f"Intelligence Router: Initiating failover to '{fallback_provider.name}'...")
            try:
                async for chunk in fallback_provider.stream(
                    messages=messages,
                    system_prompt=sys_prompt,
                    **kwargs
                ):
                    yield chunk
            except Exception as fb_exc:
                logger.exception(f"Fallback provider '{fallback_provider.name}' also failed: {fb_exc}")
                yield "MIKASA was unable to generate a response due to provider unavailability."

    async def generate(
        self,
        messages: List[Dict[str, str]],
        memory_context: Optional[str] = None,
        response_style: str = "balanced",
        routing_mode: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """Generate complete response string via the Intelligence Router."""
        collected = []
        async for chunk in self.stream(
            messages=messages,
            memory_context=memory_context,
            response_style=response_style,
            routing_mode=routing_mode,
            **kwargs
        ):
            collected.append(chunk)
        return "".join(collected)

    async def check_status(self) -> Dict[str, Any]:
        """
        Check health and status of the Intelligence Router and all configured providers.
        """
        local_status = await self.local_provider.check_status()
        online_status = await self.online_provider.check_status()

        local_ready = local_status.get("ready", False) or local_status.get("online", False)
        online_ready = online_status.get("ready", False)

        overall_ready = local_ready or online_ready
        overall_online = local_status.get("online", False) or online_status.get("online", False)

        return {
            "name": "MIKASA Intelligence Router",
            "version": config.version,
            "routing_mode": self.default_mode.value,
            "router_online": overall_online,
            "brain_online": overall_online,
            "brain_ready": overall_ready,
            "providers": {
                "local": local_status,
                "online": online_status
            }
        }

# Global singleton instance of Intelligence Router
router = IntelligenceRouter()
