import pytest
from fastapi.testclient import TestClient
from app import app
from memory.memory_service import memory_service
from storage.db import init_db

init_db()
client = TestClient(app)

def test_memory_crud():
    # 1. Add memory
    resp = client.post("/api/memory", json={"key": "Favorite Framework", "value": "FastAPI", "category": "technical"})
    assert resp.status_code == 201
    mem = resp.json()
    mid = mem["id"]
    assert mem["key"] == "Favorite Framework"
    assert mem["value"] == "FastAPI"
    
    # 2. List memories
    list_resp = client.get("/api/memory")
    assert list_resp.status_code == 200
    mems = list_resp.json()
    assert any(m["id"] == mid for m in mems)
    
    # 3. Delete memory
    del_resp = client.delete(f"/api/memory/{mid}")
    assert del_resp.status_code == 200
    
    # 4. Clear all memory
    client.post("/api/memory", json={"key": "Temp Key", "value": "Temp Value"})
    clear_resp = client.delete("/api/memory")
    assert clear_resp.status_code == 200
    assert len(client.get("/api/memory").json()) == 0

def test_memory_commands():
    # Test explicit "remember that" command
    cmd_resp = memory_service.process_user_input("Remember that I prefer Python.")
    assert cmd_resp is not None
    assert "remember" in cmd_resp.lower()
    
    # Check that memory was stored
    mems = memory_service.get_memories()
    assert any("python" in m["value"].lower() for m in mems)
    
    # Test explicit "what do you remember" query
    query_resp = memory_service.process_user_input("What do you remember about me?")
    assert query_resp is not None
    assert "Python" in query_resp
    
    # Test explicit "forget that" command
    forget_resp = memory_service.process_user_input("Forget that I prefer Python.")
    assert forget_resp is not None
    assert "forgotten" in forget_resp.lower() or "removed" in forget_resp.lower()
