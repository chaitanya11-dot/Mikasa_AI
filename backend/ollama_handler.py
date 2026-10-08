import httpx
import json
import logging
from typing import AsyncIterator, List, Dict, Any, Optional

logger = logging.getLogger("mikasa.inference")

async def check_inference_health(base_url: str, model_name: str) -> Dict[str, Any]:
    """Check if the local inference runtime is reachable and if the model is ready."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{base_url.rstrip('/')}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                model_found = any(m == model_name or m.startswith(f"{model_name}:") or model_name.startswith(m) for m in models)
                return {
                    "online": True,
                    "model_ready": model_found,
                    "available_models_count": len(models)
                }
    except Exception as exc:
        logger.debug(f"Local inference health check failed: {exc}")
        
    return {
        "online": False,
        "model_ready": False,
        "available_models_count": 0
    }

async def stream_chat_with_config(
    messages: List[Dict[str, str]],
    base_url: str,
    model: str,
    system_prompt: str,
    max_history_messages: int = 20
) -> AsyncIterator[str]:
    """Stream chat completions from local inference with robust error handling and think-tag removal."""
    url = f"{base_url.rstrip('/')}/api/chat"
    
    # Context window management: trim older messages if history is too long
    recent_msgs = messages[-max_history_messages:] if len(messages) > max_history_messages else messages
    
    formatted = [{"role": "system", "content": system_prompt}] + [
        {"role": m.get("role", "user"), "content": m.get("content", "")}
        for m in recent_msgs
        if m.get("content")
    ]
    
    payload = {
        "model": model,
        "messages": formatted,
        "stream": True,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_predict": 1024
        }
    }
    
    thinking = False
    buffer = ""
    
    try:
        # 60 second timeout for model startup / initial token
        timeout = httpx.Timeout(60.0, connect=5.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    logger.error(f"Inference HTTP {response.status_code}")
                    yield f"MIKASA local brain returned status {response.status_code}. Please check that the local model is available."
                    return
                
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    
                    raw = chunk.get("message", {}).get("content", "")
                    if raw:
                        buffer += raw
                        while True:
                            if thinking:
                                end_pos = buffer.find("</think>")
                                if end_pos < 0:
                                    buffer = ""
                                    break
                                buffer = buffer[end_pos + 8:]
                                thinking = False
                            else:
                                start_pos = buffer.find("<think>")
                                if start_pos >= 0:
                                    if start_pos > 0:
                                        yield buffer[:start_pos]
                                    buffer = buffer[start_pos + 7:]
                                    thinking = True
                                else:
                                    if buffer:
                                        yield buffer
                                    buffer = ""
                                    break
                    
                    if chunk.get("done"):
                        if buffer and not thinking:
                            yield buffer
                        break
    except httpx.ConnectError:
        logger.warning("Local inference runtime connection error.")
        yield "MIKASA's local brain is currently offline. Please ensure your local runtime is active."
    except httpx.TimeoutException:
        logger.warning("Local inference runtime timed out.")
        yield "MIKASA's local brain timed out responding. Please try your request again."
    except Exception as exc:
        logger.exception(f"Unexpected inference stream error: {exc}")
        yield "MIKASA encountered an unexpected issue while generating a response."
