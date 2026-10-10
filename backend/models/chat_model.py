from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class ChatMessage(BaseModel):
    role: str = Field(..., description="Message sender role: 'user' or 'assistant'")
    content: str = Field(..., description="Message text content")
    id: Optional[Any] = None
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="List of messages in context")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for persistence")
    response_style: Optional[str] = Field("balanced", description="Response style: concise, balanced, detailed")
    routing_mode: Optional[str] = Field(None, description="Routing mode: local_only, local_first, online_first, online_only, auto")

class ConversationCreateRequest(BaseModel):
    title: Optional[str] = Field("New Conversation", description="Title for conversation")

class ConversationUpdateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Updated conversation title")

class MemoryCreateRequest(BaseModel):
    key: str = Field(..., min_length=1, max_length=100, description="Memory key or topic")
    value: str = Field(..., min_length=1, max_length=1000, description="Memory content")
    category: Optional[str] = Field("preference", description="Memory category: preference, technical, project, general")

class SettingsUpdateRequest(BaseModel):
    theme: Optional[str] = None
    response_style: Optional[str] = None
    enter_to_send: Optional[bool] = None
    memory_enabled: Optional[bool] = None
    voice_enabled: Optional[bool] = None
    auto_speak: Optional[bool] = None
    voice_rate: Optional[float] = None
    voice_volume: Optional[float] = None
    routing_mode: Optional[str] = None
    online_model: Optional[str] = None
    online_base_url: Optional[str] = None
    online_api_key: Optional[str] = None

class VoiceSpeakRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to speak")
    options: Optional[Dict[str, Any]] = None
