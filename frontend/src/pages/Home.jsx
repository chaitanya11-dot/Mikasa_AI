import React, { useState, useEffect, useCallback, useRef } from "react";
import { useChat } from "@/hooks/useChat";
import Sidebar from "@/components/Sidebar";
import Header from "@/components/Header";
import ChatWindow from "@/components/ChatWindow";
import InputBox from "@/components/InputBox";
import SettingsModal from "@/components/SettingsModal";
import { mikasaApi } from "@/services/mikasa";
import { voiceManager } from "@/services/voice";

export default function Home({ onLogout }) {
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [isDarkMode, setDarkMode] = useState(() => {
    return localStorage.getItem("mikasa_theme") === "dark";
  });
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [history, setHistory] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [status, setStatus] = useState("mikasa-online");
  const [selectedType, setSelectedType] = useState(null);

  const [settings, setSettings] = useState({
    theme: "dark",
    response_style: "balanced",
    enter_to_send: true,
    voice_enabled: true,
    auto_speak: false,
    voice_rate: 1.0,
    voice_volume: 1.0
  });

  const settingsRef = useRef(settings);
  settingsRef.current = settings;

  const handleMessageComplete = useCallback(async (assistantText) => {
    // Auto-speak if enabled
    if (settingsRef.current.voice_enabled && settingsRef.current.auto_speak && assistantText) {
      voiceManager.speak(assistantText, {
        rate: settingsRef.current.voice_rate,
        volume: settingsRef.current.voice_volume
      });
    }

    // Refresh conversation list to pick up updated title / timestamp
    try {
      const convs = await mikasaApi.getConversations();
      setHistory(convs);
    } catch (e) {}
  }, []);

  const {
    messages,
    setMessages,
    isStreaming,
    sendMessage: rawSendMessage,
    stopGeneration,
    retryLastMessage
  } = useChat({
    activeChatId
  });

  // Initial load: settings, health, conversations
  useEffect(() => {
    const initialize = async () => {
      try {
        const [h, s, convs] = await Promise.all([
          mikasaApi.checkHealth(),
          mikasaApi.getSettings(),
          mikasaApi.getConversations()
        ]);
        setStatus(h.status);
        setSettings((prev) => ({ ...prev, ...s }));
        setHistory(convs);

        if (s.theme) {
          const isDark = s.theme === "dark";
          setDarkMode(isDark);
          localStorage.setItem("mikasa_theme", s.theme);
        }
      } catch (err) {
        console.warn("Initialization error:", err);
      }
    };
    initialize();

    // Periodic health heartbeat every 12 seconds
    const interval = setInterval(async () => {
      try {
        const h = await mikasaApi.checkHealth();
        setStatus(h.status);
      } catch (e) {
        setStatus("mikasa-offline");
      }
    }, 12000);

    return () => clearInterval(interval);
  }, []);

  // Sync theme
  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDarkMode);
    localStorage.setItem("mikasa_theme", isDarkMode ? "dark" : "light");
  }, [isDarkMode]);

  const handleNewChat = async () => {
    if (isStreaming) stopGeneration();
    voiceManager.stopSpeaking();
    setMessages([]);
    setActiveChatId(null);
    setSelectedType(null);
  };

  const handleLoadChat = async (chat) => {
    if (isStreaming) stopGeneration();
    voiceManager.stopSpeaking();
    setActiveChatId(chat.id);
    try {
      const full = await mikasaApi.getConversation(chat.id);
      setMessages(full.messages || []);
    } catch (e) {
      console.error("Failed to load conversation:", e);
    }
  };

  const handleRenameChat = async (id, newTitle) => {
    try {
      await mikasaApi.renameConversation(id, newTitle);
      setHistory((prev) =>
        prev.map((c) => (c.id === id ? { ...c, title: newTitle } : c))
      );
    } catch (e) {
      console.error("Failed to rename chat:", e);
    }
  };

  const handleDeleteChat = async (id) => {
    try {
      await mikasaApi.deleteConversation(id);
      setHistory((prev) => prev.filter((c) => c.id !== id));
      if (activeChatId === id) {
        handleNewChat();
      }
    } catch (e) {
      console.error("Failed to delete chat:", e);
    }
  };

  const handleSendMessage = async (text) => {
    let currentId = activeChatId;
    if (!currentId) {
      try {
        const created = await mikasaApi.createConversation();
        currentId = created.id;
        setActiveChatId(currentId);
        setHistory((prev) => [created, ...prev]);
      } catch (e) {
        console.warn("Failed to create conversation in backend:", e);
      }
    }

    rawSendMessage(text, {
      responseStyle: settings.response_style,
      onComplete: handleMessageComplete
    });
  };

  const handleToggleVoice = async () => {
    const nextVal = !settings.voice_enabled;
    const updated = { ...settings, voice_enabled: nextVal };
    setSettings(updated);
    if (!nextVal) {
      voiceManager.stopSpeaking();
    }
    await mikasaApi.saveSettings({ voice_enabled: nextVal });
  };

  return (
    <div className="flex h-screen bg-background text-foreground transition-colors duration-300 overflow-hidden font-sans">
      {/* Sidebar */}
      <Sidebar
        isOpen={isSidebarOpen}
        onToggle={() => setSidebarOpen(false)}
        history={history}
        activeChat={{ id: activeChatId }}
        onNewChat={handleNewChat}
        onLoadChat={handleLoadChat}
        onRenameChat={handleRenameChat}
        onDeleteChat={handleDeleteChat}
        onOpenSettings={() => setIsSettingsOpen(true)}
        status={status}
      />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col relative h-full min-w-0">
        <Header
          isSidebarOpen={isSidebarOpen}
          setSidebarOpen={setSidebarOpen}
          isDarkMode={isDarkMode}
          setDarkMode={setDarkMode}
          onLogout={onLogout}
          onOpenSettings={() => setIsSettingsOpen(true)}
          status={status}
          isStreaming={isStreaming}
          voiceEnabled={settings.voice_enabled}
          onToggleVoice={handleToggleVoice}
        />

        <div className="flex-1 flex flex-col min-h-0 relative">
          <ChatWindow
            messages={messages}
            isStreaming={isStreaming}
            selectedType={selectedType}
            onSelectType={setSelectedType}
            onQuickAction={handleSendMessage}
            onRetry={retryLastMessage}
          />
        </div>

        {/* Input Box Bar */}
        <div className="px-4 pb-6 pt-0 z-20 bg-transparent">
          <InputBox
            onSend={handleSendMessage}
            onStop={stopGeneration}
            isStreaming={isStreaming}
            enterToSend={settings.enter_to_send !== false}
          />
          <p className="text-[10px] text-center mt-3 text-muted-foreground/60 font-black uppercase tracking-widest">
            MIKASA AI • Local Sovereign Assistant v1.0.0
          </p>
        </div>
      </main>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        isDarkMode={isDarkMode}
        setDarkMode={setDarkMode}
        onDataCleared={() => {
          setHistory([]);
          handleNewChat();
        }}
      />
    </div>
  );
}
