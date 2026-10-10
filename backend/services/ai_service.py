import json
import logging
from typing import List, Dict, Any, Optional, AsyncIterator
from core.brain import brain
from memory.memory_service import memory_service
from storage.conversation_store import ConversationStore

logger = logging.getLogger("mikasa.chat")

async def get_ai_response_stream(
    messages: List[Any],
    conversation_id: Optional[str] = None,
    response_style: str = "balanced",
    routing_mode: Optional[str] = None
) -> AsyncIterator[str]:
    normalized_messages = [
        m if isinstance(m, dict) else m.model_dump()
        for m in messages
    ]
    
    if not normalized_messages:
        yield f"data: {json.dumps({'choices': [{'delta': {'content': 'How can I assist you today?'}}]})}\n\n"
        yield "data: [DONE]\n\n"
        return

    last_user_msg = ""
    for m in reversed(normalized_messages):
        if m.get("role") == "user":
            last_user_msg = m.get("content", "")
            break

    # Persist incoming user message if conversation_id provided
    if conversation_id and last_user_msg:
        try:
            ConversationStore.add_message(
                conv_id=conversation_id,
                role="user",
                content=last_user_msg
            )
        except Exception as e:
            logger.warning(f"Failed to persist user message: {e}")

    # Check for direct memory command handling
    direct_memory_resp = memory_service.process_user_input(last_user_msg) if last_user_msg else None
    
    accumulated_response = []
    
    if direct_memory_resp is not None:
        # Stream the memory system response
        payload = {
            "choices": [
                {
                    "delta": {
                        "content": direct_memory_resp
                    }
                }
            ]
        }
        accumulated_response.append(direct_memory_resp)
        yield f"data: {json.dumps(payload)}\n\n"
    else:
        # Retrieve relevant memories for prompt enrichment
        mem_context = memory_service.get_memory_context(last_user_msg) if last_user_msg else ""
        
        try:
            async for content in brain.stream(
                messages=normalized_messages,
                memory_context=mem_context,
                response_style=response_style,
                routing_mode=routing_mode
            ):
                if content:
                    accumulated_response.append(content)
                    payload = {
                        "choices": [
                            {
                                "delta": {
                                    "content": content
                                }
                            }
                        ]
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
        except Exception as exc:
            logger.exception(f"Error during brain streaming: {exc}")
            err_msg = "MIKASA encountered an issue generating this response. Please try again."
            accumulated_response.append(err_msg)
            payload = {"choices": [{"delta": {"content": err_msg}}]}
            yield f"data: {json.dumps(payload)}\n\n"

    # Persist assistant response if conversation_id is given
    if conversation_id and accumulated_response:
        full_assistant_text = "".join(accumulated_response)
        try:
            ConversationStore.add_message(
                conv_id=conversation_id,
                role="assistant",
                content=full_assistant_text
            )
        except Exception as e:
            logger.warning(f"Failed to persist assistant message: {e}")

    yield "data: [DONE]\n\n"