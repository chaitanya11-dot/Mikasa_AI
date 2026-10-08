import pytest
from fastapi.testclient import TestClient
from app import app
from storage.db import init_db

init_db()
client = TestClient(app)

def test_settings_endpoints():
    # 1. Get settings
    get_resp = client.get("/api/settings")
    assert get_resp.status_code == 200
    settings = get_resp.json()
    assert "response_style" in settings
    assert "data_path" in settings
    
    # 2. Update settings
    post_resp = client.post("/api/settings", json={"response_style": "concise", "auto_speak": True})
    assert post_resp.status_code == 200
    
    # 3. Verify updated settings
    updated = client.get("/api/settings").json()
    assert updated["response_style"] == "concise"
    assert updated["auto_speak"] is True

def test_voice_status_endpoint():
    resp = client.get("/api/voice/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "enabled" in data
