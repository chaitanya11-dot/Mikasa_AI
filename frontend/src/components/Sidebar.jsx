import React, { useState } from "react";
import { Plus, Settings, MessageSquare, MoreHorizontal, Trash2, Edit3, Search, Sparkles } from "lucide-react";

export default function Sidebar({
  history,
  activeChat,
  onNewChat,
  onLoadChat,
  onRenameChat,
  onDeleteChat,
  onOpenSettings,
  isOpen,
  status
}) {
  const [menuOpenId, setMenuOpenId] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [renamingId, setRenamingId] = useState(null);
  const [newTitle, setNewTitle] = useState("");

  const filteredHistory = history.filter((chat) =>
    (chat.title || "").toLowerCase().includes(searchQuery.toLowerCase())
  );

  const startRenaming = (chat) => {
    setRenamingId(chat.id);
    setNewTitle(chat.title);
    setMenuOpenId(null);
  };

  const submitRename = (chatId) => {
    if (newTitle.trim()) {
      onRenameChat(chatId, newTitle.trim());
    }
    setRenamingId(null);
  };

  return (
    <aside
      className={`h-screen bg-sidebar border-r border-sidebar-border flex flex-col transition-all duration-300 ${
        isOpen ? "w-72" : "w-0 overflow-hidden"
      }`}
    >
      {/* Brand Header */}
      <div className="p-5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl overflow-hidden shrink-0 shadow-md bg-white dark:bg-zinc-800 p-2 border border-border/50">
            <img src="/logo.png" alt="Mikasa Logo" className="w-full h-full object-contain" />
          </div>
          <div className="flex flex-col">
            <span className="font-black text-xl tracking-tighter leading-none">MIKASA</span>
            <span className="text-[9px] font-black uppercase tracking-[0.2em] text-orange-600 dark:text-orange-500 mt-0.5">
              Personal AI
            </span>
          </div>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="px-4 mb-3">
        <button
          onClick={onNewChat}
          className="w-full h-11 bg-white dark:bg-zinc-900 border border-border rounded-2xl flex items-center justify-center gap-2 px-4 shadow-sm hover:shadow-md hover:border-orange-500/50 transition-all group"
        >
          <Plus className="w-4 h-4 text-orange-600 transition-transform group-hover:rotate-90" />
          <span className="text-xs font-bold">New Chat</span>
        </button>
      </div>

      {/* Search Input */}
      {history.length > 2 && (
        <div className="px-4 mb-3">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground/60" />
            <input
              type="text"
              placeholder="Search chats..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full h-8 pl-8 pr-3 text-xs rounded-xl bg-accent/40 border border-border/40 focus:outline-none focus:border-orange-500/50"
            />
          </div>
        </div>
      )}

      {/* History Header */}
      <div className="px-5 mb-1.5 flex items-center justify-between">
        <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/50">
          Recent Conversations
        </span>
        <span className="text-[10px] font-mono text-muted-foreground/40">{history.length}</span>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto px-3 custom-scrollbar">
        {filteredHistory.length === 0 ? (
          <div className="p-4 text-center text-xs text-muted-foreground opacity-40 font-medium italic">
            {searchQuery ? "No matching chats" : "No conversation history yet"}
          </div>
        ) : (
          filteredHistory.map((chat) => (
            <div key={chat.id} className={`relative group mb-1 ${menuOpenId === chat.id ? "z-[60]" : "z-0"}`}>
              {renamingId === chat.id ? (
                <div className="p-1">
                  <input
                    type="text"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    onBlur={() => submitRename(chat.id)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") submitRename(chat.id);
                      if (e.key === "Escape") setRenamingId(null);
                    }}
                    autoFocus
                    className="w-full text-xs font-semibold px-3 py-2 rounded-xl bg-background border border-orange-500 focus:outline-none"
                  />
                </div>
              ) : (
                <button
                  onClick={() => onLoadChat(chat)}
                  className={`w-full text-left p-2.5 pr-10 rounded-xl text-xs font-semibold transition-all flex items-center gap-2.5 truncate border ${
                    activeChat?.id === chat.id
                      ? "bg-white dark:bg-zinc-800 border-border shadow-sm text-foreground font-bold"
                      : "text-muted-foreground border-transparent hover:bg-accent/50 hover:text-foreground"
                  }`}
                >
                  <MessageSquare
                    className={`w-3.5 h-3.5 shrink-0 ${
                      activeChat?.id === chat.id ? "text-orange-500" : "opacity-40"
                    }`}
                  />
                  <span className="truncate">{chat.title || "Untitled Conversation"}</span>
                </button>
              )}

              {renamingId !== chat.id && (
                <div className="absolute right-1 top-1/2 -translate-y-1/2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setMenuOpenId(menuOpenId === chat.id ? null : chat.id);
                    }}
                    className={`p-1.5 rounded-lg hover:bg-accent transition-opacity ${
                      activeChat?.id === chat.id || menuOpenId === chat.id
                        ? "opacity-100"
                        : "opacity-0 group-hover:opacity-100"
                    }`}
                  >
                    <MoreHorizontal className="w-3.5 h-3.5" />
                  </button>

                  {menuOpenId === chat.id && (
                    <>
                      <div
                        className="fixed inset-0 z-[70] cursor-default"
                        onClick={(e) => {
                          e.stopPropagation();
                          setMenuOpenId(null);
                        }}
                      />
                      <div className="absolute right-0 top-full mt-1 min-w-[140px] bg-white dark:bg-zinc-900 border border-border rounded-2xl shadow-xl z-[80] p-1.5 overflow-hidden animate-in fade-in zoom-in duration-100 origin-top-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            startRenaming(chat);
                          }}
                          className="w-full flex items-center justify-between p-2 text-[10px] font-black uppercase tracking-wider text-muted-foreground hover:text-foreground hover:bg-accent rounded-xl transition-all"
                        >
                          <span>Rename</span>
                          <Edit3 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onDeleteChat(chat.id);
                            setMenuOpenId(null);
                          }}
                          className="w-full flex items-center justify-between p-2 text-[10px] font-black uppercase tracking-wider text-red-500 hover:bg-red-500/10 rounded-xl transition-all"
                        >
                          <span>Delete</span>
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Footer Settings & Status */}
      <div className="p-3 border-t border-border space-y-2">
        <button
          onClick={onOpenSettings}
          className="w-full h-10 flex items-center gap-2.5 px-3 rounded-xl text-muted-foreground hover:text-foreground hover:bg-accent transition-all text-xs font-bold"
        >
          <Settings className="w-4 h-4 opacity-70" />
          <span>Settings</span>
        </button>

        <div className="px-3 py-1.5 flex items-center justify-between text-[10px] text-muted-foreground/60 border-t border-border/30 pt-2 font-mono">
          <div className="flex items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full ${
                status === "mikasa-online" ? "bg-green-500" : "bg-red-500"
              }`}
            />
            <span>{status === "mikasa-online" ? "MIKASA Online" : "Offline"}</span>
          </div>
          <span>v1.0.0</span>
        </div>
      </div>
    </aside>
  );
}
