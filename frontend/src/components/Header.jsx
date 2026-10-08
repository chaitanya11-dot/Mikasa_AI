import React, { useState } from "react";
import { Menu, Sun, Moon, LogOut, Shield, ChevronDown, Settings, Volume2, VolumeX } from "lucide-react";

export default function Header({
  isSidebarOpen,
  setSidebarOpen,
  isDarkMode,
  setDarkMode,
  onLogout,
  onOpenSettings,
  status,
  isStreaming,
  voiceEnabled,
  onToggleVoice
}) {
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  return (
    <header className="h-14 flex items-center justify-between px-5 bg-transparent z-40 transition-all relative border-b border-border/40">
      {/* Left section: Sidebar toggle & Status Indicator */}
      <div className="flex items-center gap-3">
        {!isSidebarOpen && (
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 hover:bg-accent rounded-xl text-muted-foreground transition-all"
            title="Open Sidebar"
          >
            <Menu className="w-4 h-4" />
          </button>
        )}

        {/* Status Indicator */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-accent/40 border border-border/40 text-xs font-semibold">
          <span
            className={`w-2 h-2 rounded-full ${
              isStreaming
                ? "bg-orange-500 animate-ping"
                : status === "mikasa-online"
                ? "bg-green-500"
                : "bg-red-500"
            }`}
          />
          <span className="text-[11px] font-bold text-foreground/80">
            {isStreaming
              ? "MIKASA Generating..."
              : status === "mikasa-online"
              ? "MIKASA Online"
              : "MIKASA Offline"}
          </span>
        </div>
      </div>

      {/* Right controls */}
      <div className="flex items-center gap-2">
        {/* Voice Toggle */}
        <button
          onClick={onToggleVoice}
          className={`p-2 rounded-xl transition-all ${
            voiceEnabled
              ? "text-orange-500 hover:bg-orange-500/10"
              : "text-muted-foreground opacity-50 hover:bg-accent"
          }`}
          title={voiceEnabled ? "Voice Enabled" : "Voice Muted"}
        >
          {voiceEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
        </button>

        {/* Dark/Light mode */}
        <button
          onClick={() => setDarkMode(!isDarkMode)}
          className="p-2 hover:bg-accent rounded-xl transition-all text-muted-foreground hover:text-foreground"
          title="Toggle Theme"
        >
          {isDarkMode ? <Sun className="w-4 h-4 text-orange-500" /> : <Moon className="w-4 h-4" />}
        </button>

        {/* Settings Button */}
        <button
          onClick={onOpenSettings}
          className="p-2 hover:bg-accent rounded-xl transition-all text-muted-foreground hover:text-foreground"
          title="Open Settings"
        >
          <Settings className="w-4 h-4" />
        </button>

        {/* Profile Dropdown */}
        <div className="relative">
          <button
            onClick={() => setIsProfileOpen(!isProfileOpen)}
            className={`flex items-center gap-1.5 p-1 rounded-full border border-border transition-all hover:shadow-sm ${
              isProfileOpen ? "bg-accent" : "bg-background hover:bg-accent/50"
            }`}
          >
            <div className="w-7 h-7 rounded-full bg-orange-500/10 flex items-center justify-center text-orange-600 overflow-hidden text-xs font-black">
              M
            </div>
            <ChevronDown
              className={`w-3.5 h-3.5 text-muted-foreground transition-transform mr-1 ${
                isProfileOpen ? "rotate-180" : ""
              }`}
            />
          </button>

          {isProfileOpen && (
            <>
              <div className="fixed inset-0 z-30" onClick={() => setIsProfileOpen(false)} />
              <div className="absolute right-0 top-full mt-2 w-60 bg-white dark:bg-zinc-900 border border-border rounded-2xl shadow-2xl z-40 p-3 animate-in fade-in slide-in-from-top-2 duration-150">
                <div className="flex items-center gap-3 pb-3 mb-2 border-b border-border">
                  <div className="w-9 h-9 rounded-xl bg-orange-600 flex items-center justify-center text-white font-black text-sm shadow-md shadow-orange-600/20">
                    M
                  </div>
                  <div>
                    <h4 className="font-bold text-xs">Pilot User</h4>
                    <p className="text-[9px] uppercase font-black tracking-widest text-muted-foreground/60">
                      Local Sovereign Session
                    </p>
                  </div>
                </div>

                <div className="space-y-1">
                  <button
                    onClick={() => {
                      setIsProfileOpen(false);
                      onOpenSettings();
                    }}
                    className="w-full flex items-center gap-2.5 p-2 rounded-xl text-xs font-semibold hover:bg-accent transition-all text-left"
                  >
                    <Settings className="w-4 h-4 text-orange-500" />
                    Assistant Settings
                  </button>
                  <button
                    onClick={() => {
                      setIsProfileOpen(false);
                      onLogout();
                    }}
                    className="w-full flex items-center gap-2.5 p-2 rounded-xl text-xs font-semibold hover:bg-red-500/10 text-red-500 transition-all text-left"
                  >
                    <LogOut className="w-4 h-4" />
                    Logout Session
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
