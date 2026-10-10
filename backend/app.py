import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.config import config
from core.brain import brain
from storage.db import init_db
from storage.conversation_store import ConversationStore
from memory.memory_store import MemoryStore

from routes.chat_routes import router as chat_router
from routes.conversation_routes import router as conversation_router
from routes.memory_routes import router as memory_router
from routes.voice_routes import router as voice_router
from routes.settings_routes import router as settings_router, load_persisted_settings_into_runtime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("mikasa.core")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    load_persisted_settings_into_runtime()
    
    logger.info("=========================================")
    logger.info(f" MIKASA Core v{config.version} Starting...")
    logger.info(f" Architecture: Intelligence Router (V2.1)")
    logger.info(f" Routing Mode: {config.routing_mode}")
    logger.info(f" Host: {config.host}:{config.port}")
    logger.info("=========================================")
    logger.info("Local SQLite database initialized & settings synchronized.")
    
    status = await brain.check_status()
    if status.get("brain_online") or status.get("brain_ready"):
        logger.info(f"MIKASA Intelligence Router: Online & Operational (Mode: {status.get('mode', 'local')})")
    else:
        logger.warning("MIKASA Intelligence Router: Local & Online providers currently unreachable")
        
    yield
    
    logger.info("MIKASA Core shutting down cleanly.")

app = FastAPI(title="MIKASA Core", version=config.version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(conversation_router)
app.include_router(memory_router)
app.include_router(voice_router)
app.include_router(settings_router)

@app.get("/api/health")
async def health():
    brain_status = await brain.check_status()
    is_online = brain_status.get("brain_online", False) or brain_status.get("brain_ready", False)
    
    # Simple count of conversations and memories
    try:
        convs = ConversationStore.get_conversations()
        mems = MemoryStore.get_all_memories()
        conv_count = len(convs)
        mem_count = len(mems)
    except Exception:
        conv_count = 0
        mem_count = 0
        
    return {
        "status": "mikasa-online" if is_online else "mikasa-offline",
        "name": "MIKASA",
        "version": config.version,
        "mode": "local",
        "brain_ready": is_online,
        "routing_mode": brain_status.get("mode", "local_only"),
        "providers": brain_status.get("router", {}).get("providers", {}),
        "conversation_count": conv_count,
        "memory_count": mem_count
    }

@app.get("/api/core")
async def core_info():
    return {
        "name": "MIKASA",
        "version": config.version,
        "mode": "local",
        "routing_mode": config.routing_mode,
        "transport": "intelligence-router"
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host=config.host, port=config.port, reload=True)
