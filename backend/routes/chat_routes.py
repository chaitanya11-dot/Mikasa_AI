from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.chat_model import ChatRequest
from services.ai_service import get_ai_response_stream

router = APIRouter(tags=["chat"])

@router.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    return StreamingResponse(
        get_ai_response_stream(
            messages=request.messages,
            conversation_id=request.conversation_id,
            response_style=request.response_style or "balanced",
            routing_mode=request.routing_mode
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
