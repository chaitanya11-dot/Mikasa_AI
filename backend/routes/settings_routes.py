from fastapi import APIRouter
from typing import Dict, Any
from storage.db import get_connection, get_db_path
from models.chat_model import SettingsUpdateRequest
from voice.voice_config import voice_config
import os
import json

from core.router.intelligence_router import router as intelligence_router, RoutingMode
from core.config import config

router = APIRouter(prefix="/api/settings", tags=["settings"])

DEFAULT_SETTINGS = {
    "theme": "dark",
    "response_style": "balanced",
    "enter_to_send": True,
    "memory_enabled": True,
    "voice_enabled": True,
    "auto_speak": False,
    "voice_rate": 1.0,
    "voice_volume": 1.0,
    "local_mode": True,
    "routing_mode": config.routing_mode,
    "online_model": config.online_model,
    "online_base_url": config.online_base_url,
    "router_fallback": config.router_fallback
}

@router.get("")
async def get_settings() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    rows = cursor.fetchall()
    conn.close()
    
    settings = dict(DEFAULT_SETTINGS)
    for r in rows:
        try:
            settings[r["key"]] = json.loads(r["value"])
        except Exception:
            settings[r["key"]] = r["value"]
            
    # Include data path and voice status
    settings["data_path"] = os.path.dirname(get_db_path())
    return settings

@router.post("")
async def update_settings(req: SettingsUpdateRequest):
    updates = req.model_dump(exclude_unset=True)
    if not updates:
        return {"status": "ok"}
        
    conn = get_connection()
    cursor = conn.cursor()
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    
    for key, val in updates.items():
        if val is not None:
            # Sync with runtime configs if applicable
            if key == "voice_enabled":
                voice_config.enabled = bool(val)
            elif key == "auto_speak":
                voice_config.auto_speak = bool(val)
            elif key == "voice_rate":
                voice_config.rate = float(val)
            elif key == "voice_volume":
                voice_config.volume = float(val)
            elif key == "routing_mode":
                intelligence_router.default_mode = RoutingMode.normalize(str(val))
                
            cursor.execute(
                "INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
                (key, json.dumps(val), now)
            )
            
    conn.commit()
    conn.close()
    return {"status": "ok", "updated": list(updates.keys())}

@router.delete("/data")
async def clear_all_local_data():
    """Clear all local conversations and memory database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages")
    cursor.execute("DELETE FROM conversations")
    cursor.execute("DELETE FROM memory")
    conn.commit()
    conn.close()
    return {"status": "ok", "message": "All local conversations and memories cleared"}
