from typing import List, Dict, Any, Optional
from memory.memory_store import MemoryStore
from memory.memory_extractor import MemoryExtractor

class MemoryService:
    @staticmethod
    def get_memories() -> List[Dict[str, Any]]:
        return MemoryStore.get_all_memories()

    @staticmethod
    def add_memory(key: str, value: str, category: str = "preference") -> Dict[str, Any]:
        return MemoryStore.add_memory(key, value, category)

    @staticmethod
    def delete_memory(mem_id: str) -> bool:
        return MemoryStore.delete_memory(mem_id)

    @staticmethod
    def clear_memories() -> bool:
        return MemoryStore.clear_all_memories()

    @staticmethod
    def process_user_input(user_input: str) -> Optional[str]:
        """
        Process user input for explicit memory commands.
        If it is a memory command, returns the direct response string.
        Otherwise extracts any implicit memory and returns None.
        """
        is_command, response = MemoryExtractor.handle_explicit_commands(user_input)
        if is_command:
            return response
            
        # Try extracting implicit memories in background
        try:
            MemoryExtractor.extract_implicit_memories(user_input)
        except Exception:
            pass
        return None

    @staticmethod
    def get_memory_context(query: str, limit: int = 5) -> str:
        """
        Get formatted memory context block for injection into the MIKASA prompt.
        Only returns relevant memories to prevent context bloat.
        """
        memories = MemoryStore.get_relevant_memories(query, limit=limit)
        if not memories:
            return ""
            
        lines = ["\n[USER RECALLED MEMORIES]"]
        for m in memories:
            lines.append(f"- {m['key']}: {m['value']}")
        lines.append("Use the above user memories naturally if relevant to the conversation.\n")
        return "\n".join(lines)

memory_service = MemoryService()
