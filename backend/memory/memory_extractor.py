import re
from typing import Optional, Tuple, Dict, Any, List
from memory.memory_store import MemoryStore

class MemoryExtractor:
    @staticmethod
    def handle_explicit_commands(user_input: str) -> Tuple[bool, Optional[str]]:
        """
        Check if user input is an explicit memory command (remember, forget, query memories).
        Returns (is_command, response_text).
        """
        text = user_input.strip()
        lower_text = text.lower()
        
        # 1. Query memories: "what do you remember about me?", "show my memories", "what do you know about me"
        if re.search(r'\b(what do you remember|what are my memories|what do you know about me|show (my|the) memories)\b', lower_text):
            memories = MemoryStore.get_all_memories()
            if not memories:
                return True, "I don't have any saved memories about you yet. You can tell me things like 'Remember that I prefer Python' and I'll keep them in mind."
            
            lines = ["Here is what I remember about you:"]
            for m in memories:
                lines.append(f"• **{m['key']}**: {m['value']}")
            return True, "\n".join(lines)
            
        # 2. Check for statements ending with "remember that" / "remember this" / "keep that in mind"
        # e.g., "My favorite programming language is Python. Remember that."
        ending_remember = re.search(r'^(.*?)[\.\,\;\s]+(?:remember\s+(?:that|this)|keep\s+that\s+in\s+mind)[\.\!]?$', text, re.IGNORECASE)
        if ending_remember:
            fact = ending_remember.group(1).strip().rstrip('.!?')
            if fact:
                key, value, category = MemoryExtractor.categorize_fact(fact)
                MemoryStore.add_memory(key=key, value=value, category=category)
                return True, f"Understood. I will remember that: **{fact}**."

        # 3. Explicit Forget command: "forget that [fact]", "forget [fact]", "remove memory about [fact]"
        forget_match = re.search(r'\b(?:forget\s+(?:that\s+)?|remove\s+memory\s+(?:about\s+)?)(.+)', text, re.IGNORECASE)
        if forget_match:
            target = forget_match.group(1).strip().rstrip('.!?')
            count = MemoryStore.delete_memory_by_keyword(target)
            if count > 0:
                return True, f"I have forgotten that: *{target}*."
            else:
                words = [w for w in target.split() if len(w) > 3 and w.lower() not in {"that", "about", "prefer", "like"}]
                deleted = 0
                for w in words:
                    deleted += MemoryStore.delete_memory_by_keyword(w)
                if deleted > 0:
                    return True, f"I have removed the memory related to *{target}*."
                return True, f"I couldn't find a stored memory matching *{target}* to forget."

        # 4. Explicit Remember command: "remember that [fact]", "remember: [fact]", "please remember [fact]"
        remember_match = re.search(r'^(?:please\s+)?remember\s+(?:that\s+|:\s*)?(.+)', text, re.IGNORECASE)
        if remember_match:
            fact = remember_match.group(1).strip().rstrip('.!?')
            if fact and fact.lower() not in {"that", "this", "it"}:
                key, value, category = MemoryExtractor.categorize_fact(fact)
                MemoryStore.add_memory(key=key, value=value, category=category)
                return True, f"I'll remember that: **{fact}**."

        return False, None

    @staticmethod
    def categorize_fact(fact: str) -> Tuple[str, str, str]:
        """Categorize a fact into key, value, category."""
        clean_fact = fact.strip()
        lower = clean_fact.lower()
        
        # Language preference
        if "programming language" in lower or "language is" in lower or "code in" in lower or "python" in lower or "javascript" in lower or "rust" in lower or "golang" in lower or "c++" in lower:
            return "Preferred Programming Language", clean_fact, "preference"
        # Framework / Tech stack
        if "framework" in lower or "database" in lower or "stack" in lower or "react" in lower or "fastapi" in lower:
            return "Tech Stack", clean_fact, "technical"
        # Projects
        if "project" in lower or "working on" in lower or "building" in lower:
            return "Current Project", clean_fact, "project"
        # Name / Identity
        if "my name is" in lower or "call me" in lower:
            return "User Name", clean_fact, "identity"
        # General preference
        if "i prefer" in lower or "i like" in lower or "my favorite" in lower:
            return "User Preference", clean_fact, "preference"
            
        return "User Fact", clean_fact, "general"

    @staticmethod
    def extract_implicit_memories(user_input: str):
        """Extract subtle preferences from regular conversation without interrupting flow."""
        text = user_input.strip()
        
        patterns = [
            (r'\bmy\s+favorite\s+programming\s+language\s+is\s+([a-zA-Z\+\#]+)\b', "Preferred Programming Language", "preference"),
            (r'\bi\s+prefer\s+programming\s+in\s+([a-zA-Z\+\#]+)\b', "Preferred Programming Language", "preference"),
            (r'\bi\s+usually\s+work\s+with\s+([a-zA-Z\+\#\.\s]+)\b', "Tech Stack", "technical"),
            (r'\bmy\s+name\s+is\s+([A-Z][a-zA-Z]+)\b', "User Name", "identity"),
        ]
        
        for pat, key, cat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                val = text.strip()
                MemoryStore.add_memory(key=key, value=val, category=cat)
                break
