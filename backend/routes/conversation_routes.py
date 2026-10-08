from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from storage.conversation_store import ConversationStore
from models.chat_model import ConversationCreateRequest, ConversationUpdateRequest

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

@router.get("", response_model=List[Dict[str, Any]])
async def list_conversations():
    return ConversationStore.get_conversations()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_conversation(req: ConversationCreateRequest = None):
    title = req.title if req else "New Conversation"
    return ConversationStore.create_conversation(title=title)

@router.get("/{conv_id}")
async def get_conversation(conv_id: str):
    conv = ConversationStore.get_conversation(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

@router.patch("/{conv_id}")
async def rename_conversation(conv_id: str, req: ConversationUpdateRequest):
    success = ConversationStore.update_title(conv_id, req.title)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "ok", "id": conv_id, "title": req.title}

@router.delete("/{conv_id}")
async def delete_conversation(conv_id: str):
    success = ConversationStore.delete_conversation(conv_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "ok", "deleted": True}

@router.post("/{conv_id}/clear")
async def clear_conversation(conv_id: str):
    success = ConversationStore.clear_messages(conv_id)
    return {"status": "ok", "cleared": True}
