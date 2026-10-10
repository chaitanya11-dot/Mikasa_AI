const API_BASE = import.meta.env.VITE_MIKASA_CORE_URL || "http://127.0.0.1:8000";

export const mikasaApi = {
  // Health and status
  async checkHealth() {
    try {
      const res = await fetch(`${API_BASE}/api/health`, { method: "GET" });
      if (!res.ok) throw new Error(`Health check HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      return {
        status: "mikasa-offline",
        name: "MIKASA",
        version: "1.0.0",
        mode: "local",
        brain_ready: false
      };
    }
  },

  // Conversations
  async getConversations() {
    try {
      const res = await fetch(`${API_BASE}/api/conversations`);
      if (!res.ok) throw new Error("Failed to fetch conversations");
      return await res.json();
    } catch (err) {
      console.warn("Failed to fetch conversations from MIKASA Core:", err);
      return [];
    }
  },

  async createConversation(title = "New Conversation") {
    const res = await fetch(`${API_BASE}/api/conversations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title })
    });
    if (!res.ok) throw new Error("Failed to create conversation");
    return await res.json();
  },

  async getConversation(id) {
    const res = await fetch(`${API_BASE}/api/conversations/${id}`);
    if (!res.ok) throw new Error("Failed to load conversation");
    return await res.json();
  },

  async renameConversation(id, title) {
    const res = await fetch(`${API_BASE}/api/conversations/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title })
    });
    if (!res.ok) throw new Error("Failed to rename conversation");
    return await res.json();
  },

  async deleteConversation(id) {
    const res = await fetch(`${API_BASE}/api/conversations/${id}`, {
      method: "DELETE"
    });
    if (!res.ok) throw new Error("Failed to delete conversation");
    return await res.json();
  },

  async clearConversation(id) {
    const res = await fetch(`${API_BASE}/api/conversations/${id}/clear`, {
      method: "POST"
    });
    if (!res.ok) throw new Error("Failed to clear conversation");
    return await res.json();
  },

  // Memory
  async getMemories() {
    try {
      const res = await fetch(`${API_BASE}/api/memory`);
      if (!res.ok) throw new Error("Failed to fetch memories");
      return await res.json();
    } catch (err) {
      console.warn("Memory fetch error:", err);
      return [];
    }
  },

  async addMemory(key, value, category = "preference") {
    const res = await fetch(`${API_BASE}/api/memory`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key, value, category })
    });
    if (!res.ok) throw new Error("Failed to add memory");
    return await res.json();
  },

  async deleteMemory(id) {
    const res = await fetch(`${API_BASE}/api/memory/${id}`, {
      method: "DELETE"
    });
    if (!res.ok) throw new Error("Failed to delete memory");
    return await res.json();
  },

  async clearMemories() {
    const res = await fetch(`${API_BASE}/api/memory`, {
      method: "DELETE"
    });
    if (!res.ok) throw new Error("Failed to clear memory");
    return await res.json();
  },

  // Settings
  async getSettings() {
    try {
      const res = await fetch(`${API_BASE}/api/settings`);
      if (!res.ok) throw new Error("Failed to load settings");
      return await res.json();
    } catch (err) {
      return {
        theme: "dark",
        response_style: "balanced",
        enter_to_send: true,
        memory_enabled: true,
        voice_enabled: true,
        auto_speak: false,
        voice_rate: 1.0,
        voice_volume: 1.0
      };
    }
  },

  async saveSettings(settings) {
    const res = await fetch(`${API_BASE}/api/settings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settings)
    });
    if (!res.ok) throw new Error("Failed to update settings");
    return await res.json();
  },

  async clearLocalData() {
    const res = await fetch(`${API_BASE}/api/settings/data`, {
      method: "DELETE"
    });
    if (!res.ok) throw new Error("Failed to clear local data");
    return await res.json();
  },

  // Voice Status
  async getVoiceStatus() {
    try {
      const res = await fetch(`${API_BASE}/api/voice/status`);
      if (!res.ok) throw new Error("Failed to get voice status");
      return await res.json();
    } catch (err) {
      return { enabled: false, provider: "none" };
    }
  },

  // Robust SSE Chat Stream
  async streamChat({
    messages,
    conversationId,
    responseStyle = "balanced",
    routingMode,
    signal,
    onDelta,
    onComplete,
    onError
  }) {
    try {
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages,
          conversation_id: conversationId,
          response_style: responseStyle,
          routing_mode: routingMode
        }),
        signal
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      if (!response.body) {
        throw new Error("No response body received from MIKASA Core");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      let isDone = false;

      while (!isDone) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        // Save uncompleted partial line for next iteration
        buffer = lines.pop() || "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || !trimmed.startsWith("data:")) continue;

          const dataStr = trimmed.slice(5).trim();
          if (dataStr === "[DONE]") {
            isDone = true;
            break;
          }

          try {
            const parsed = JSON.parse(dataStr);
            const delta = parsed?.choices?.[0]?.delta?.content;
            if (delta) {
              onDelta(delta);
            }
          } catch (jsonErr) {
            // Ignore partial non-JSON line fragments
          }
        }
      }

      // Flush remainder
      if (buffer.trim()) {
        const remaining = buffer.trim();
        if (remaining.startsWith("data:")) {
          const dataStr = remaining.slice(5).trim();
          if (dataStr !== "[DONE]") {
            try {
              const parsed = JSON.parse(dataStr);
              const delta = parsed?.choices?.[0]?.delta?.content;
              if (delta) onDelta(delta);
            } catch (e) {}
          }
        }
      }

      onComplete();
    } catch (err) {
      if (err.name === "AbortError") {
        onComplete();
      } else {
        console.error("MIKASA Stream Error:", err);
        onError(err);
      }
    }
  }
};
