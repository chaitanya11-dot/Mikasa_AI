import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from storage.db import get_connection

class MemoryStore:
    @staticmethod
    def add_memory(key: str, value: str, category: str = "preference", mem_id: Optional[str] = None) -> Dict[str, Any]:
        mid = mem_id or str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if identical key exists, update if so
        cursor.execute("SELECT id FROM memory WHERE LOWER(key) = LOWER(?)", (key.strip(),))
        existing = cursor.fetchone()
        
        if existing:
            mid = existing["id"]
            cursor.execute(
                "UPDATE memory SET value = ?, category = ?, updated_at = ? WHERE id = ?",
                (value.strip(), category.strip(), now, mid)
            )
        else:
            cursor.execute(
                "INSERT INTO memory (id, key, value, category, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (mid, key.strip(), value.strip(), category.strip(), now, now)
            )
        conn.commit()
        conn.close()
        return {"id": mid, "key": key.strip(), "value": value.strip(), "category": category, "created_at": now, "updated_at": now}

    @staticmethod
    def get_all_memories() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, key, value, category, created_at, updated_at FROM memory ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r["id"],
                "key": r["key"],
                "value": r["value"],
                "category": r["category"],
                "created_at": r["created_at"],
                "updated_at": r["updated_at"]
            }
            for r in rows
        ]

    @staticmethod
    def delete_memory(mem_id: str) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memory WHERE id = ?", (mem_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    @staticmethod
    def delete_memory_by_keyword(keyword: str) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM memory WHERE LOWER(key) LIKE LOWER(?) OR LOWER(value) LIKE LOWER(?)",
            (f"%{keyword}%", f"%{keyword}%")
        )
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted_count

    @staticmethod
    def clear_all_memories() -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memory")
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_relevant_memories(query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve memories relevant to the current user query."""
        all_mems = MemoryStore.get_all_memories()
        if not all_mems:
            return []
            
        words = set(w.lower() for w in query.split() if len(w) > 2)
        scored = []
        for mem in all_mems:
            mem_text = f"{mem['key']} {mem['value']} {mem['category']}".lower()
            score = 0
            for w in words:
                if w in mem_text:
                    score += 1
            # Give base score so recent/important memories are included if query is broad
            scored.append((score, mem))
            
        # If any matched specifically, sort by match score; else return most recent
        scored.sort(key=lambda x: (x[0], x[1]["updated_at"]), reverse=True)
        return [item[1] for item in scored[:limit]]
