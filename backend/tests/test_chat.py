import pytest
from fastapi.testclient import TestClient
from app import app
from storage.db import init_db

init_db()
client = TestClient(app)

def test_chat_stream_format():
    # Send a chat request
    req_body = {
        "messages": [
            {"role": "user", "content": "Remember that I love coding in Python."}
        ]
    }
    resp = client.post("/api/chat", json=req_body)
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    
    text = resp.text
    assert "data: " in text
    assert "data: [DONE]" in text
