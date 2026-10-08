import { useState, useRef, useCallback } from "react";
import { mikasaApi } from "@/services/mikasa";

export function useChat({ activeChatId, onConversationCreated } = {}) {
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const abortControllerRef = useRef(null);

  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  const sendMessage = useCallback(
    async (text, options = {}) => {
      if (!text || !text.trim() || isStreaming) return;

      setError(null);
      const userText = text.trim();
      const userMsg = {
        id: `user-${Date.now()}`,
        role: "user",
        content: userText,
        timestamp: new Date().toISOString()
      };

      const newMsgs = [...messages, userMsg];
      setMessages(newMsgs);
      setIsStreaming(true);

      const aiMsgId = `assistant-${Date.now() + 1}`;
      const aiPlaceholder = {
        id: aiMsgId,
        role: "assistant",
        content: "",
        timestamp: new Date().toISOString()
      };

      setMessages((prev) => [...prev, aiPlaceholder]);

      abortControllerRef.current = new AbortController();
      let accumulated = "";

      await mikasaApi.streamChat({
        messages: newMsgs,
        conversationId: activeChatId,
        responseStyle: options.responseStyle || "balanced",
        signal: abortControllerRef.current.signal,
        onDelta: (delta) => {
          accumulated += delta;
          setMessages((prev) => {
            const copy = [...prev];
            const lastIdx = copy.length - 1;
            if (lastIdx >= 0 && copy[lastIdx].id === aiMsgId) {
              copy[lastIdx] = { ...copy[lastIdx], content: accumulated };
            }
            return copy;
          });
        },
        onComplete: () => {
          setIsStreaming(false);
          abortControllerRef.current = null;
          if (options.onComplete) {
            options.onComplete(accumulated);
          }
        },
        onError: (err) => {
          setIsStreaming(false);
          abortControllerRef.current = null;
          setError("MIKASA is currently offline or encountered a network error.");
          setMessages((prev) => {
            const copy = [...prev];
            const lastIdx = copy.length - 1;
            if (lastIdx >= 0 && copy[lastIdx].id === aiMsgId) {
              copy[lastIdx] = {
                ...copy[lastIdx],
                content:
                  accumulated ||
                  "MIKASA is currently offline or unreachable. Please verify that MIKASA Core is running."
              };
            }
            return copy;
          });
        }
      });
    },
    [messages, isStreaming, activeChatId]
  );

  const retryLastMessage = useCallback(() => {
    if (messages.length < 2 || isStreaming) return;
    // Find last user message
    let lastUserIndex = -1;
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === "user") {
        lastUserIndex = i;
        break;
      }
    }

    if (lastUserIndex === -1) return;

    const userText = messages[lastUserIndex].content;
    const historyBefore = messages.slice(0, lastUserIndex);
    setMessages(historyBefore);
    sendMessage(userText);
  }, [messages, isStreaming, sendMessage]);

  return {
    messages,
    setMessages,
    isStreaming,
    error,
    sendMessage,
    stopGeneration,
    retryLastMessage
  };
}
