import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from app import app
from core.router.intelligence_router import IntelligenceRouter, RoutingMode, RoutingDecision
from core.providers.base import BaseIntelligenceProvider
from core.providers.local_provider import LocalMikasaProvider
from core.providers.online_provider import OnlineMikasaProvider
from core.brain import MikasaBrain
from storage.db import init_db

init_db()
client = TestClient(app)

class MockProvider(BaseIntelligenceProvider):
    def __init__(self, name: str, ptype: str, should_fail: bool = False, tokens: list = None):
        self._name = name
        self._ptype = ptype
        self.should_fail = should_fail
        self.tokens = tokens or ["Hello", " from ", name]

    @property
    def name(self) -> str:
        return self._name

    @property
    def provider_type(self) -> str:
        return self._ptype

    async def stream(self, messages, system_prompt, **kwargs):
        if self.should_fail:
            raise RuntimeError(f"Simulated failure in {self._name}")
        for t in self.tokens:
            yield t

    async def check_status(self):
        return {
            "provider": self._name,
            "type": self._ptype,
            "online": not self.should_fail,
            "ready": not self.should_fail
        }

def test_router_local_only_mode():
    async def _test():
        local_p = MockProvider("mock_local", "local")
        online_p = MockProvider("mock_online", "online")
        router = IntelligenceRouter(local_provider=local_p, online_provider=online_p, default_mode=RoutingMode.LOCAL_ONLY)

        decision = await router.evaluate_route([{"role": "user", "content": "Hello"}])
        assert decision.selected_engine == "local"
        assert decision.mode == RoutingMode.LOCAL_ONLY
        assert decision.fallback_available is False

        tokens = []
        async for t in router.stream([{"role": "user", "content": "Hello"}]):
            tokens.append(t)
        assert "".join(tokens) == "Hello from mock_local"

    asyncio.run(_test())

def test_router_online_only_mode():
    async def _test():
        local_p = MockProvider("mock_local", "local")
        online_p = MockProvider("mock_online", "online")
        router = IntelligenceRouter(local_provider=local_p, online_provider=online_p, default_mode=RoutingMode.ONLINE_ONLY)

        decision = await router.evaluate_route([{"role": "user", "content": "Hello"}])
        assert decision.selected_engine == "online"
        assert decision.mode == RoutingMode.ONLINE_ONLY

        tokens = []
        async for t in router.stream([{"role": "user", "content": "Hello"}]):
            tokens.append(t)
        assert "".join(tokens) == "Hello from mock_online"

    asyncio.run(_test())

def test_router_failover_local_to_online():
    async def _test():
        local_p = MockProvider("mock_local", "local", should_fail=True)
        online_p = OnlineMikasaProvider(api_key="test-key", model="gpt-4o-mini")
        
        async def mock_online_stream(messages, system_prompt, **kwargs):
            yield "Online "
            yield "Fallback"
        online_p.stream = mock_online_stream

        router = IntelligenceRouter(local_provider=local_p, online_provider=online_p, default_mode=RoutingMode.LOCAL_FIRST)

        tokens = []
        async for t in router.stream([{"role": "user", "content": "Test failover"}]):
            tokens.append(t)

        assert "".join(tokens) == "Online Fallback"

    asyncio.run(_test())

def test_router_auto_mode_heuristics():
    async def _test():
        local_p = MockProvider("mock_local", "local")
        online_p = OnlineMikasaProvider(api_key="test-key", model="gpt-4o-mini")
        router = IntelligenceRouter(local_provider=local_p, online_provider=online_p, default_mode=RoutingMode.AUTO)

        # Standard query -> local
        decision_std = await router.evaluate_route([{"role": "user", "content": "What is the weather?"}])
        assert decision_std.selected_engine == "local"

        # Architecture / complex query -> online
        decision_complex = await router.evaluate_route([{"role": "user", "content": "Please design the architecture design for distributed microservices"}])
        assert decision_complex.selected_engine == "online"

        # Very long context (> 3000 chars) -> online
        long_msg = "Explain " + ("x" * 3500)
        decision_long = await router.evaluate_route([{"role": "user", "content": long_msg}])
        assert decision_long.selected_engine == "online"

    asyncio.run(_test())

def test_brain_facade_delegation():
    async def _test():
        local_p = MockProvider("brain_local", "local")
        online_p = MockProvider("brain_online", "online")
        router = IntelligenceRouter(local_provider=local_p, online_provider=online_p, default_mode=RoutingMode.LOCAL_ONLY)
        custom_brain = MikasaBrain(intelligence_router=router)

        response = await custom_brain.generate([{"role": "user", "content": "Hi Mikasa"}])
        assert response == "Hello from brain_local"

        status = await custom_brain.check_status()
        assert status["name"] == "MIKASA"
        assert status["brain_online"] is True
        assert "providers" in status["router"]

    asyncio.run(_test())

def test_chat_endpoint_with_routing_mode():
    req_body = {
        "messages": [
            {"role": "user", "content": "Hello MIKASA router test"}
        ],
        "routing_mode": "local_only"
    }
    resp = client.post("/api/chat", json=req_body)
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]

def test_settings_routing_mode_update():
    # Update routing mode via settings API
    update_payload = {
        "routing_mode": "auto",
        "online_model": "gpt-4o-mini"
    }
    resp = client.post("/api/settings", json=update_payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

    # Verify settings persistence
    get_resp = client.get("/api/settings")
    assert get_resp.status_code == 200
    settings_data = get_resp.json()
    assert settings_data["routing_mode"] == "auto"
    assert settings_data["online_model"] == "gpt-4o-mini"

    # Reset back to local_only
    client.post("/api/settings", json={"routing_mode": "local_only"})
