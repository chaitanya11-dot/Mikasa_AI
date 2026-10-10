import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  X,
  Sliders,
  Brain,
  Volume2,
  ShieldCheck,
  Cpu,
  Trash2,
  Plus,
  Play,
  RotateCcw,
  Check,
  AlertTriangle
} from "lucide-react";
import { mikasaApi } from "@/services/mikasa";
import { voiceManager } from "@/services/voice";

export default function SettingsModal({ isOpen, onClose, isDarkMode, setDarkMode, onDataCleared }) {
  const [activeTab, setActiveTab] = useState("general");
  const [settings, setSettings] = useState({
    theme: "dark",
    response_style: "balanced",
    enter_to_send: true,
    memory_enabled: true,
    voice_enabled: true,
    auto_speak: false,
    voice_rate: 1.0,
    voice_volume: 1.0,
    data_path: "./data"
  });

  const [memories, setMemories] = useState([]);
  const [newKey, setNewKey] = useState("");
  const [newVal, setNewVal] = useState("");
  const [newCat, setNewCat] = useState("preference");
  const [healthStatus, setHealthStatus] = useState(null);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [isTestingVoice, setIsTestingVoice] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadSettingsAndData();
    }
  }, [isOpen]);

  const loadSettingsAndData = async () => {
    try {
      const [s, m, h] = await Promise.all([
        mikasaApi.getSettings(),
        mikasaApi.getMemories(),
        mikasaApi.checkHealth()
      ]);
      setSettings((prev) => ({ ...prev, ...s }));
      setMemories(m);
      setHealthStatus(h);
    } catch (e) {
      console.error("Failed to load settings data:", e);
    }
  };

  const handleSaveSetting = async (key, val) => {
    const updated = { ...settings, [key]: val };
    setSettings(updated);
    try {
      await mikasaApi.saveSettings({ [key]: val });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 1500);
    } catch (e) {
      console.error("Failed to save setting:", e);
    }
  };

  const handleAddMemory = async (e) => {
    e.preventDefault();
    if (!newKey.trim() || !newVal.trim()) return;
    try {
      const created = await mikasaApi.addMemory(newKey.trim(), newVal.trim(), newCat);
      setMemories((prev) => [created, ...prev]);
      setNewKey("");
      setNewVal("");
    } catch (e) {
      console.error("Failed to add memory:", e);
    }
  };

  const handleDeleteMemory = async (id) => {
    try {
      await mikasaApi.deleteMemory(id);
      setMemories((prev) => prev.filter((m) => m.id !== id));
    } catch (e) {
      console.error("Failed to delete memory:", e);
    }
  };

  const handleClearAllMemories = async () => {
    if (window.confirm("Are you sure you want to clear all stored memories?")) {
      try {
        await mikasaApi.clearMemories();
        setMemories([]);
      } catch (e) {
        console.error("Failed to clear memories:", e);
      }
    }
  };

  const handleClearAllData = async () => {
    if (
      window.confirm(
        "Are you sure you want to completely erase all local conversations, messages, and memories? This cannot be undone."
      )
    ) {
      try {
        await mikasaApi.clearLocalData();
        setMemories([]);
        if (onDataCleared) onDataCleared();
        alert("All local data has been successfully cleared.");
      } catch (e) {
        console.error("Failed to clear local data:", e);
      }
    }
  };

  const handleTestVoice = () => {
    setIsTestingVoice(true);
    voiceManager.speak("Hello, I am MIKASA. Your authorized voice engine is operational and ready.", {
      rate: settings.voice_rate,
      volume: settings.voice_volume,
      onEnd: () => setIsTestingVoice(false),
      onError: () => setIsTestingVoice(false)
    });
  };

  if (!isOpen) return null;

  const tabs = [
    { id: "general", label: "General", icon: Sliders },
    { id: "memory", label: "Memory", icon: Brain },
    { id: "voice", label: "Voice", icon: Volume2 },
    { id: "privacy", label: "Privacy & Data", icon: ShieldCheck },
    { id: "system", label: "System & Status", icon: Cpu }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="w-full max-w-2xl bg-white dark:bg-zinc-900 border border-border rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]"
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-accent/30">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-orange-600/10 text-orange-600 flex items-center justify-center font-bold">
              <Sliders className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-lg font-black tracking-tight">MIKASA Settings</h2>
              <p className="text-[10px] uppercase font-black tracking-widest text-muted-foreground/60">
                Local Assistant Configuration
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {saveSuccess && (
              <span className="text-xs font-semibold text-green-500 flex items-center gap-1">
                <Check className="w-3.5 h-3.5" /> Saved
              </span>
            )}
            <button
              onClick={onClose}
              className="p-2 hover:bg-accent rounded-xl text-muted-foreground transition-all"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 flex overflow-hidden">
          {/* Tabs Sidebar */}
          <div className="w-48 border-r border-border p-3 space-y-1 bg-accent/10">
            {tabs.map((t) => {
              const Icon = t.icon;
              return (
                <button
                  key={t.id}
                  onClick={() => setActiveTab(t.id)}
                  className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-xs font-bold transition-all text-left ${
                    activeTab === t.id
                      ? "bg-orange-600 text-white shadow-md shadow-orange-600/20"
                      : "text-muted-foreground hover:bg-accent hover:text-foreground"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{t.label}</span>
                </button>
              );
            })}
          </div>

          {/* Tab Content */}
          <div className="flex-1 p-6 overflow-y-auto custom-scrollbar space-y-6 text-sm">
            {/* 1. GENERAL TAB */}
            {activeTab === "general" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-sm font-black uppercase tracking-wider text-muted-foreground/70 mb-3">
                    Interface Theme
                  </h3>
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      onClick={() => {
                        setDarkMode(false);
                        handleSaveSetting("theme", "light");
                      }}
                      className={`p-3.5 rounded-2xl border flex items-center justify-between font-bold text-xs transition-all ${
                        !isDarkMode
                          ? "border-orange-500 bg-orange-50 dark:bg-orange-950/20 text-orange-600"
                          : "border-border hover:bg-accent"
                      }`}
                    >
                      <span>Light Theme</span>
                      {!isDarkMode && <Check className="w-4 h-4" />}
                    </button>
                    <button
                      onClick={() => {
                        setDarkMode(true);
                        handleSaveSetting("theme", "dark");
                      }}
                      className={`p-3.5 rounded-2xl border flex items-center justify-between font-bold text-xs transition-all ${
                        isDarkMode
                          ? "border-orange-500 bg-orange-50 dark:bg-orange-950/20 text-orange-600"
                          : "border-border hover:bg-accent"
                      }`}
                    >
                      <span>Dark Theme</span>
                      {isDarkMode && <Check className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-black uppercase tracking-wider text-muted-foreground/70 mb-3">
                    MIKASA Response Style
                  </h3>
                  <div className="grid grid-cols-3 gap-2">
                    {["concise", "balanced", "detailed"].map((style) => (
                      <button
                        key={style}
                        onClick={() => handleSaveSetting("response_style", style)}
                        className={`p-3 rounded-2xl border text-xs font-bold capitalize transition-all ${
                          settings.response_style === style
                            ? "border-orange-500 bg-orange-50 dark:bg-orange-950/20 text-orange-600"
                            : "border-border hover:bg-accent"
                        }`}
                      >
                        {style}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-black uppercase tracking-wider text-muted-foreground/70 mb-3">
                    Intelligence Router (V2.1)
                  </h3>
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      { id: "local_only", label: "Local Only" },
                      { id: "local_first", label: "Local First" },
                      { id: "auto", label: "Auto Smart" },
                      { id: "online_first", label: "Online First" },
                      { id: "online_only", label: "Online Only" }
                    ].map((mode) => (
                      <button
                        key={mode.id}
                        onClick={() => handleSaveSetting("routing_mode", mode.id)}
                        className={`p-3 rounded-2xl border text-xs font-bold transition-all ${
                          (settings.routing_mode || "local_only") === mode.id
                            ? "border-orange-500 bg-orange-50 dark:bg-orange-950/20 text-orange-600"
                            : "border-border hover:bg-accent"
                        }`}
                      >
                        {mode.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-between p-4 rounded-2xl border border-border bg-accent/20">
                  <div>
                    <h4 className="font-bold text-xs">Enter to Send</h4>
                    <p className="text-[11px] text-muted-foreground">Press Enter to send message, Shift+Enter for newline</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.enter_to_send !== false}
                    onChange={(e) => handleSaveSetting("enter_to_send", e.target.checked)}
                    className="w-5 h-5 accent-orange-600 rounded cursor-pointer"
                  />
                </div>
              </div>
            )}

            {/* 2. MEMORY TAB */}
            {activeTab === "memory" && (
              <div className="space-y-6">
                <div className="flex items-center justify-between p-4 rounded-2xl border border-border bg-accent/20">
                  <div>
                    <h4 className="font-bold text-xs">MIKASA Memory</h4>
                    <p className="text-[11px] text-muted-foreground">Remember user preferences and context locally</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.memory_enabled !== false}
                    onChange={(e) => handleSaveSetting("memory_enabled", e.target.checked)}
                    className="w-5 h-5 accent-orange-600 rounded cursor-pointer"
                  />
                </div>

                {/* Add new memory */}
                <form onSubmit={handleAddMemory} className="p-4 rounded-2xl border border-border bg-accent/10 space-y-3">
                  <h4 className="text-xs font-black uppercase tracking-wider text-muted-foreground/70">
                    Add Explicit Memory
                  </h4>
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="text"
                      placeholder="Topic (e.g., Preferred Language)"
                      value={newKey}
                      onChange={(e) => setNewKey(e.target.value)}
                      className="px-3 py-2 bg-background border border-border rounded-xl text-xs font-semibold focus:outline-none focus:border-orange-500"
                    />
                    <select
                      value={newCat}
                      onChange={(e) => setNewCat(e.target.value)}
                      className="px-3 py-2 bg-background border border-border rounded-xl text-xs font-semibold focus:outline-none focus:border-orange-500"
                    >
                      <option value="preference">Preference</option>
                      <option value="technical">Technical</option>
                      <option value="project">Project</option>
                      <option value="general">General</option>
                    </select>
                  </div>
                  <input
                    type="text"
                    placeholder="Memory fact (e.g., User prefers Python 3.12 for backend)"
                    value={newVal}
                    onChange={(e) => setNewVal(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-xl text-xs font-semibold focus:outline-none focus:border-orange-500"
                  />
                  <button
                    type="submit"
                    className="w-full py-2 bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 rounded-xl font-bold text-xs hover:opacity-90 flex items-center justify-center gap-1.5"
                  >
                    <Plus className="w-3.5 h-3.5" /> Save Memory
                  </button>
                </form>

                {/* List of memories */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-xs font-black uppercase tracking-wider text-muted-foreground/70">
                      Stored Memories ({memories.length})
                    </h4>
                    {memories.length > 0 && (
                      <button
                        onClick={handleClearAllMemories}
                        className="text-[11px] font-bold text-red-500 hover:underline flex items-center gap-1"
                      >
                        <Trash2 className="w-3 h-3" /> Clear All
                      </button>
                    )}
                  </div>
                  {memories.length === 0 ? (
                    <div className="p-6 text-center text-xs text-muted-foreground bg-accent/20 rounded-2xl italic">
                      No memories stored yet. MIKASA can remember your preferences automatically or when you ask.
                    </div>
                  ) : (
                    <div className="space-y-2 max-h-48 overflow-y-auto custom-scrollbar pr-1">
                      {memories.map((m) => (
                        <div
                          key={m.id}
                          className="p-3 bg-accent/30 border border-border rounded-xl flex items-center justify-between gap-2"
                        >
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center gap-2">
                              <span className="font-bold text-xs text-foreground">{m.key}</span>
                              <span className="text-[9px] uppercase px-1.5 py-0.5 rounded-full bg-orange-500/10 text-orange-600 font-bold">
                                {m.category}
                              </span>
                            </div>
                            <p className="text-xs text-muted-foreground truncate mt-0.5">{m.value}</p>
                          </div>
                          <button
                            onClick={() => handleDeleteMemory(m.id)}
                            className="p-1.5 hover:bg-red-500/10 text-muted-foreground hover:text-red-500 rounded-lg transition-all"
                            title="Delete memory"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* 3. VOICE TAB */}
            {activeTab === "voice" && (
              <div className="space-y-6">
                <div className="flex items-center justify-between p-4 rounded-2xl border border-border bg-accent/20">
                  <div>
                    <h4 className="font-bold text-xs">Voice Output</h4>
                    <p className="text-[11px] text-muted-foreground">Enable speech synthesis for MIKASA</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.voice_enabled !== false}
                    onChange={(e) => handleSaveSetting("voice_enabled", e.target.checked)}
                    className="w-5 h-5 accent-orange-600 rounded cursor-pointer"
                  />
                </div>

                <div className="flex items-center justify-between p-4 rounded-2xl border border-border bg-accent/20">
                  <div>
                    <h4 className="font-bold text-xs">Auto-Speak Responses</h4>
                    <p className="text-[11px] text-muted-foreground">Automatically speak new assistant responses</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={Boolean(settings.auto_speak)}
                    onChange={(e) => handleSaveSetting("auto_speak", e.target.checked)}
                    className="w-5 h-5 accent-orange-600 rounded cursor-pointer"
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-xs font-bold">
                    <span>Speech Rate (Speed)</span>
                    <span className="text-orange-600 font-mono">{settings.voice_rate || 1.0}x</span>
                  </div>
                  <input
                    type="range"
                    min="0.5"
                    max="1.75"
                    step="0.05"
                    value={settings.voice_rate || 1.0}
                    onChange={(e) => handleSaveSetting("voice_rate", parseFloat(e.target.value))}
                    className="w-full accent-orange-600 cursor-pointer"
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-xs font-bold">
                    <span>Volume</span>
                    <span className="text-orange-600 font-mono">{Math.round((settings.voice_volume || 1.0) * 100)}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={settings.voice_volume || 1.0}
                    onChange={(e) => handleSaveSetting("voice_volume", parseFloat(e.target.value))}
                    className="w-full accent-orange-600 cursor-pointer"
                  />
                </div>

                <button
                  onClick={handleTestVoice}
                  disabled={isTestingVoice}
                  className="w-full py-3 bg-orange-600 hover:bg-orange-500 text-white rounded-2xl font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-orange-600/20 transition-all disabled:opacity-50"
                >
                  <Play className="w-4 h-4" />
                  {isTestingVoice ? "Speaking Authorized Voice..." : "Test MIKASA Voice"}
                </button>
              </div>
            )}

            {/* 4. PRIVACY TAB */}
            {activeTab === "privacy" && (
              <div className="space-y-6">
                <div className="p-4 rounded-2xl border border-green-500/30 bg-green-500/5 space-y-2">
                  <div className="flex items-center gap-2 text-green-600 font-bold text-xs">
                    <ShieldCheck className="w-4 h-4" />
                    <span>Local-First Sovereign Architecture</span>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    MIKASA processes your queries locally using your system's hardware. Your conversations, memories,
                    and personal data are never sent to external cloud providers.
                  </p>
                </div>

                <div>
                  <h4 className="text-xs font-black uppercase tracking-wider text-muted-foreground/70 mb-2">
                    Storage Location
                  </h4>
                  <div className="p-3 bg-accent/40 border border-border rounded-xl font-mono text-xs text-muted-foreground break-all">
                    {settings.data_path || "./data"}
                  </div>
                </div>

                <div className="p-4 rounded-2xl border border-red-500/20 bg-red-500/5 space-y-3">
                  <div className="flex items-center gap-2 text-red-500 font-bold text-xs">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Danger Zone</span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Erase all local conversation logs, messages, and memory records from your local database.
                  </p>
                  <button
                    onClick={handleClearAllData}
                    className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-xl font-bold text-xs transition-all shadow-sm flex items-center gap-1.5"
                  >
                    <Trash2 className="w-3.5 h-3.5" /> Clear All Local Data
                  </button>
                </div>
              </div>
            )}

            {/* 5. SYSTEM TAB */}
            {activeTab === "system" && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-4 rounded-2xl border border-border bg-accent/20">
                    <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
                      MIKASA Status
                    </span>
                    <div className="flex items-center gap-2 mt-1">
                      <span
                        className={`w-2.5 h-2.5 rounded-full ${
                          healthStatus?.status === "mikasa-online" ? "bg-green-500 animate-pulse" : "bg-red-500"
                        }`}
                      />
                      <span className="font-bold text-sm">
                        {healthStatus?.status === "mikasa-online" ? "Online" : "Offline"}
                      </span>
                    </div>
                  </div>

                  <div className="p-4 rounded-2xl border border-border bg-accent/20">
                    <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
                      Brain Readiness
                    </span>
                    <div className="flex items-center gap-2 mt-1">
                      <span
                        className={`w-2.5 h-2.5 rounded-full ${
                          healthStatus?.brain_ready ? "bg-green-500" : "bg-yellow-500"
                        }`}
                      />
                      <span className="font-bold text-sm">
                        {healthStatus?.brain_ready ? "Operational" : "Initializing"}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="p-4 rounded-2xl border border-border bg-accent/20 space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="font-bold text-muted-foreground">MIKASA Version</span>
                    <span className="font-mono font-bold">{healthStatus?.version || "1.0.0"}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="font-bold text-muted-foreground">Local Mode</span>
                    <span className="font-bold text-green-600">Active</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="font-bold text-muted-foreground">Total Conversations</span>
                    <span className="font-bold">{healthStatus?.conversation_count || 0}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="font-bold text-muted-foreground">Total Memories</span>
                    <span className="font-bold">{healthStatus?.memory_count || 0}</span>
                  </div>
                </div>

                <button
                  onClick={loadSettingsAndData}
                  className="w-full py-2.5 bg-accent hover:bg-accent/80 border border-border rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition-all"
                >
                  <RotateCcw className="w-3.5 h-3.5" /> Refresh Diagnostics
                </button>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
