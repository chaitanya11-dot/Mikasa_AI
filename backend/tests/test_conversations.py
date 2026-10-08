import pytest
from fastapi.testclient import TestClient
from app import app
from storage.db import init_db

init_db()
client = TestClient(app)

def test_conversation_lifecycle():
    # 1. Create conversation
    create_resp = client.post("/api/conversations", json={"title": "Test Chat"})
    assert create_resp.status_code == 201
    conv = create_resp.json()
    cid = conv["id"]
    assert conv["title"] == "Test Chat"
    
    # 2. List conversations
    list_resp = client.get("/api/conversations")
    assert list_resp.status_code == 200
    convs = list_resp.json()
    assert any(c["id"] == cid for c in convs)
    
    # 3. Get single conversation
    get_resp = client.get(f"/api/conversations/{cid}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == cid
    
    # 4. Rename conversation
    patch_resp = client.patch(f"/api/conversations/{cid}", json={"title": "Renamed Chat"})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["title"] == "Renamed Chat"
    
    # 5. Clear conversation messages
    clear_resp = client.post(f"/api/conversations/{cid}/clear")
    assert clear_resp.status_code == 200
    
    # 6. Delete conversation
    del_resp = client.delete(f"/api/conversations/{cid}")
    assert del_resp.status_code == 200
    
    # 7. Verify deletion
    get_del_resp = client.get(f"/api/conversations/{cid}")
    assert get_del_resp.status_code == 404
