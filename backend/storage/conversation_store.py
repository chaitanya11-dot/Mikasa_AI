import uuid
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from storage.db import get_connection

def generate_title_from_text(text: str) -> str:
    """Generate a clean, concise 2-6 word conversation title from the first message."""
    clean = re.sub(r'[^\w\s\-\?\.]', '', text).strip()
    words = clean.split()
    if not words:
        return "New Conversation"
    
    # Strip common leading question / polite phrases
    strip_starters = ["can you", "could you", "please", "help me with", "tell me about", "what is", "how do i", "explain", "write a", "write an"]
    lower_clean = clean.lower()
    for starter in strip_starters:
        if lower_clean.startswith(starter):
            trimmed = clean[len(starter):].strip()
            if trimmed:
                words = trimmed.split()
            break
            
    title_words = words[:5]
    title = " ".join(title_words).strip().capitalize()
    if len(title) > 40:
        title = title[:37] + "..."
    return title or "New Conversation"

class ConversationStore:
    @staticmethod
    def create_conversation(title: Optional[str] = None, conv_id: Optional[str] = None) -> Dict[str, Any]:
        cid = conv_id or str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        t = title or "New Conversation"
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (cid, t, now, now)
        )
        conn.commit()
        conn.close()
        return {"id": cid, "title": t, "created_at": now, "updated_at": now, "messages": []}

    @staticmethod
    def get_conversations() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.title, c.created_at, c.updated_at, COUNT(m.id) as message_count
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.conversation_id
            GROUP BY c.id
            ORDER BY c.updated_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r["id"],
                "title": r["title"],
                "created_at": r["created_at"],
                "updated_at": r["updated_at"],
                "message_count": r["message_count"]
            }
            for r in rows
        ]

    @staticmethod
    def get_conversation(conv_id: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, created_at, updated_at FROM conversations WHERE id = ?", (conv_id,))
        conv_row = cursor.fetchone()
        if not conv_row:
            conn.close()
            return None
        
        cursor.execute(
            "SELECT id, role, content, timestamp FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC",
            (conv_id,)
        )
        msg_rows = cursor.fetchall()
        conn.close()
        
        messages = [
            {
                "id": m["id"],
                "role": m["role"],
                "content": m["content"],
                "timestamp": m["timestamp"]
            }
            for m in msg_rows
        ]
        return {
            "id": conv_row["id"],
            "title": conv_row["title"],
            "created_at": conv_row["created_at"],
            "updated_at": conv_row["updated_at"],
            "messages": messages
        }

    @staticmethod
    def update_title(conv_id: str, title: str) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
            (title.strip(), now, conv_id)
        )
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated

    @staticmethod
    def delete_conversation(conv_id: str) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    @staticmethod
    def add_message(conv_id: str, role: str, content: str, msg_id: Optional[str] = None) -> Dict[str, Any]:
        # Ensure conversation exists
        conv = ConversationStore.get_conversation(conv_id)
        if not conv:
            ConversationStore.create_conversation(conv_id=conv_id)
            
        mid = msg_id or str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (id, conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?, ?)",
            (mid, conv_id, role, content, now)
        )
        # Update conversation updated_at and title if first user message
        if conv and len(conv.get("messages", [])) == 0 and role == "user":
            new_title = generate_title_from_text(content)
            cursor.execute(
                "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
                (new_title, now, conv_id)
            )
        else:
            cursor.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (now, conv_id)
            )
        conn.commit()
        conn.close()
        return {"id": mid, "conversation_id": conv_id, "role": role, "content": content, "timestamp": now}

    @staticmethod
    def clear_messages(conv_id: str) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
        cursor.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conv_id))
        conn.commit()
        conn.close()
        return True
