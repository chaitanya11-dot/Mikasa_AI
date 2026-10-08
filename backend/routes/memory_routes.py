from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from memory.memory_service import memory_service
from models.chat_model import MemoryCreateRequest

router = APIRouter(prefix="/api/memory", tags=["memory"])

@router.get("", response_model=List[Dict[str, Any]])
async def get_memories():
    return memory_service.get_memories()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_memory(req: MemoryCreateRequest):
    return memory_service.add_memory(key=req.key, value=req.value, category=req.category)

@router.delete("/{mem_id}")
async def delete_single_memory(mem_id: str):
    success = memory_service.delete_memory(mem_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory item not found")
    return {"status": "ok", "deleted": True}

@router.delete("")
async def clear_all_memory():
    memory_service.clear_memories()
    return {"status": "ok", "cleared": True}
