import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from app import app
from core.router.intelligence_router import IntelligenceRouter, RoutingMode, RoutingDecision
from core.providers.base import BaseIntelligenceProvider
from core.providers.local_provider import LocalMikasaProvider
from core.providers.online_provider import OnlineMikasaProvider, OnlineProviderError
from core.brain import MikasaBrain
from storage.db import init_db, get_connection
from storage.conversation_store import ConversationStore
from memory.memory_store import MemoryStore
from routes.settings_routes import load_persisted_settings_into_runtime
from services.ai_service import get_ai_response_stream

init_db()
client = TestClient(app)

class MockStreamProvider(BaseIntelligenceProvider):
    def __init__(
        self,
        name: str,
        ptype: str,
        chunks: list = None,
        fail_at_chunk: int = -1,
        initial_exception: Exception = None,
        configured: bool = True
    ):
        self._name = name
        self._ptype = ptype
        self.chunks = chunks or ["Hello", " from ", name]
        self.fail_at_chunk = fail_at_chunk
        self.initial_exception = initial_exception
        self.configured = configured
        self.call_count = 0
        self.received_messages = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def provider_type(self) -> str:
        return self._ptype

    @property
    def is_configured(self) -> bool:
        return self.configured

    async def stream(self, messages, system_prompt, **kwargs):
        self.call_count += 1
        self.received_messages = messages
        if self.initial_exception:
            raise self.initial_exception
        
        for idx, c in enumerate(self.chunks):
            if self.fail_at_chunk == idx:
                raise RuntimeError(f"Mid-stream failure in {self._name} at chunk {idx}")
            yield c

    async def check_status(self):
        return {
            "provider": self._name,
            "type": self._ptype,
            "online": True,
            "ready": True
        }


# =====================================================================
# 1. Local-Only Operation
# =====================================================================
def test_local_only_operation():
    """Verify MIKASA chats, accesses local memory and saves conversations locally with no internet."""
    async def _test():
        # 1. Set up local memory
        MemoryStore.add_memory("user_pet", "Dog named Rusty", category="fact")
        
        # 2. Create conversation
        conv = ConversationStore.create_conversation(title="Test Local Chat")
        conv_id = conv["id"]

        local_provider = MockStreamProvider("local_mikasa", "local", chunks=["Local ", "response ", "acknowledged."])
        online_provider = MockStreamProvider("online_mikasa", "online")

        router = IntelligenceRouter(
            local_provider=local_provider,
            online_provider=online_provider,
            default_mode=RoutingMode.LOCAL_ONLY
        )

        # Stream response
        messages = [{"role": "user", "content": "What is my pet?"}]
        tokens = []
        async for chunk in router.stream(messages=messages, routing_mode="local_only"):
            tokens.append(chunk)

        full_resp = "".join(tokens)
        assert full_resp == "Local response acknowledged."
        assert local_provider.call_count == 1
        assert online_provider.call_count == 0  # Zero online calls

        # Verify conversation saving
        ConversationStore.add_message(conv_id, "user", "What is my pet?")
        ConversationStore.add_message(conv_id, "assistant", full_resp)
        
        saved_conv = ConversationStore.get_conversation(conv_id)
        assert saved_conv is not None
        saved_msgs = saved_conv["messages"]
        assert len(saved_msgs) == 2
        assert saved_msgs[0]["content"] == "What is my pet?"
        assert saved_msgs[1]["content"] == "Local response acknowledged."

        # Verify local memory retrieval
        all_mems = MemoryStore.get_all_memories()
        pet_mem = next((m for m in all_mems if m["key"] == "user_pet"), None)
        assert pet_mem is not None
        assert pet_mem["value"] == "Dog named Rusty"

    asyncio.run(_test())


# =====================================================================
# 2. Online Provider Failure & Safe Fallback / Clear Error
# =====================================================================
def test_online_provider_failure_with_safe_fallback():
    """Simulate online provider 401/timeout/error in ONLINE_FIRST and verify safe local fallback."""
    async def _test():
        local_provider = MockStreamProvider("local_mikasa", "local", chunks=["Fallback ", "local ", "response"])
        online_provider = MockStreamProvider(
            "online_mikasa",
            "online",
            initial_exception=OnlineProviderError("Online provider authorization failed (HTTP 401).")
        )

        router = IntelligenceRouter(
            local_provider=local_provider,
            online_provider=online_provider,
            default_mode=RoutingMode.ONLINE_FIRST
        )

        tokens = []
        async for chunk in router.stream([{"role": "user", "content": "Hello online"}]):
            tokens.append(chunk)

        full_resp = "".join(tokens)
        # Online failed -> seamless fallback to local
        assert full_resp == "Fallback local response"
        assert online_provider.call_count == 1
        assert local_provider.call_count == 1

    asyncio.run(_test())


def test_online_provider_failure_in_online_only_mode():
    """Simulate online provider failure in ONLINE_ONLY mode and verify clear error message."""
    async def _test():
        local_provider = MockStreamProvider("local_mikasa", "local", chunks=["Local"])
        online_provider = MockStreamProvider(
            "online_mikasa",
            "online",
            initial_exception=OnlineProviderError("Online provider request timed out.")
        )

        router = IntelligenceRouter(
            local_provider=local_provider,
            online_provider=online_provider,
            default_mode=RoutingMode.ONLINE_ONLY
        )

        tokens = []
        async for chunk in router.stream([{"role": "user", "content": "Hello online only"}]):
            tokens.append(chunk)

        full_resp = "".join(tokens)
        assert "error" in full_resp.lower()
        assert "timed out" in full_resp.lower()
        assert local_provider.call_count == 0  # No fallback in ONLINE_ONLY

    asyncio.run(_test())


# =====================================================================
# 3. Streaming Failover & Interruption (No duplicates, valid SSE)
# =====================================================================
def test_streaming_interruption_prevents_duplicate_text():
    """Interrupt provider mid-response and ensure fallback is not triggered mid-stream to avoid duplicates."""
    async def _test():
        # Local provider yields 2 chunks and then fails on 3rd chunk
        local_provider = MockStreamProvider(
            "local_mikasa",
            "local",
            chunks=["First ", "Second ", "Third"],
            fail_at_chunk=2
        )
        online_provider = MockStreamProvider(
            "online_mikasa",
            "online",
            chunks=["Online ", "full ", "answer"]
        )

        router = IntelligenceRouter(
            local_provider=local_provider,
            online_provider=online_provider,
            default_mode=RoutingMode.LOCAL_FIRST
        )

        tokens = []
        async for chunk in router.stream([{"role": "user", "content": "Stream test"}]):
            tokens.append(chunk)

        full_resp = "".join(tokens)
        # Should contain the initial chunks without repeating online response from start
        assert full_resp == "First Second "
        assert online_provider.call_count == 0  # Crucial: did not re-trigger fallback

    asyncio.run(_test())


def test_ai_service_sse_stream_validity_and_termination():
    """Verify that get_ai_response_stream outputs valid SSE events and terminates with data: [DONE]."""
    async def _test():
        messages = [{"role": "user", "content": "Test SSE"}]
        events = []
        async for event in get_ai_response_stream(messages, routing_mode="local_only"):
            events.append(event)

        assert len(events) >= 1
        # Check that each event is valid SSE format
        for ev in events:
            assert ev.startswith("data: ")
            assert ev.endswith("\n\n")

        # Last event must be [DONE]
        assert events[-1] == "data: [DONE]\n\n"

    asyncio.run(_test())


# =====================================================================
# 4. Privacy Enforcement (Local-Only strict isolation)
# =====================================================================
def test_privacy_enforcement_local_isolation():
    """Verify that in LOCAL_ONLY mode, sensitive prompts and private memory are NEVER sent to online provider."""
    async def _test():
        sensitive_prompt = "My secret banking password is 12345-SUPER-SECRET"
        local_provider = MockStreamProvider("local_mikasa", "local", chunks=["Secured local processing."])
        online_provider = MockStreamProvider("online_mikasa", "online")

        router = IntelligenceRouter(
            local_provider=local_provider,
            online_provider=online_provider,
            default_mode=RoutingMode.LOCAL_ONLY
        )

        decision = await router.evaluate_route([{"role": "user", "content": sensitive_prompt}])
        assert decision.selected_engine == "local"
        assert decision.fallback_available is False
        assert decision.fallback_engine is None

        tokens = []
        async for chunk in router.stream([{"role": "user", "content": sensitive_prompt}]):
            tokens.append(chunk)

        assert "".join(tokens) == "Secured local processing."
        assert online_provider.call_count == 0
        assert len(online_provider.received_messages) == 0

    asyncio.run(_test())


# =====================================================================
# 5. Settings Persistence across Restarts
# =====================================================================
def test_settings_persistence_across_restart():
    """Verify chosen routing mode and provider configuration persist in SQLite and load into runtime on restart."""
    # 1. Update settings via API
    update_payload = {
        "routing_mode": "online_first",
        "online_model": "claude-3-5-sonnet",
        "online_base_url": "https://api.anthropic.com/v1",
        "router_fallback": True
    }
    resp = client.post("/api/settings", json=update_payload)
    assert resp.status_code == 200

    # 2. Verify saved in DB
    get_resp = client.get("/api/settings")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["routing_mode"] == "online_first"
    assert data["online_model"] == "claude-3-5-sonnet"
    assert data["online_base_url"] == "https://api.anthropic.com/v1"

    # 3. Simulate backend restart: Re-trigger load_persisted_settings_into_runtime()
    load_persisted_settings_into_runtime()

    from core.router.intelligence_router import router as global_router
    from core.config import config

    assert global_router.default_mode == RoutingMode.ONLINE_FIRST
    assert config.routing_mode == "online_first"
    assert config.online_model == "claude-3-5-sonnet"

    # Clean up: Reset back to local_only
    client.post("/api/settings", json={"routing_mode": "local_only", "online_model": "gpt-4o-mini"})
    load_persisted_settings_into_runtime()
