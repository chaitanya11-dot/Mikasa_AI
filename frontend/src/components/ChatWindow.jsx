import React, { useRef, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Code, Brain, Sparkles, Terminal, ChevronDown } from "lucide-react";
import MessageBubble from "./MessageBubble";
import Loader from "./Loader";

export default function ChatWindow({
  messages,
  isStreaming,
  selectedType,
  onSelectType,
  onQuickAction,
  onRetry
}) {
  const viewportRef = useRef(null);
  const [showScrollBottom, setShowScrollBottom] = useState(false);

  const scrollToBottom = (behavior = "smooth") => {
    if (viewportRef.current) {
      viewportRef.current.scrollTo({
        top: viewportRef.current.scrollHeight,
        behavior
      });
    }
  };

  useEffect(() => {
    scrollToBottom("smooth");
  }, [messages, isStreaming]);

  const handleScroll = () => {
    if (!viewportRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = viewportRef.current;
    const isUp = scrollHeight - scrollTop - clientHeight > 120;
    setShowScrollBottom(isUp);
  };

  const quickActions = [
    {
      title: "Architect a Project",
      prompt: "Help me design a clean and modular architecture for a modern web application.",
      desc: "Design scalable modular systems & APIs",
      icon: Code,
      color: "text-orange-500"
    },
    {
      title: "Analyze & Reason",
      prompt: "Explain how binary search trees work and analyze their time complexity.",
      desc: "Extract insights & solve algorithms",
      icon: Brain,
      color: "text-orange-600"
    },
    {
      title: "Creative Scribe",
      prompt: "Draft a clear, high-impact product announcement for MIKASA AI Assistant.",
      desc: "Draft polished copy & documentation",
      icon: Sparkles,
      color: "text-amber-500"
    },
    {
      title: "Debug & Optimize",
      prompt: "Write a Python function to check whether a number is prime and explain edge cases.",
      desc: "Diagnose logic bottlenecks & optimize code",
      icon: Terminal,
      color: "text-orange-700"
    }
  ];

  return (
    <div
      ref={viewportRef}
      onScroll={handleScroll}
      className="flex-1 overflow-y-auto custom-scrollbar flex flex-col pt-2 min-h-0 relative"
    >
      {messages.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-3xl mx-auto w-full">
          <motion.div
            initial={{ opacity: 0, scale: 0.85 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-20 h-20 xl:w-24 xl:h-24 mb-5"
          >
            <img src="/logo.png" alt="Mikasa Logo" className="w-full h-full object-contain" />
          </motion.div>

          <h1 className="text-3xl xl:text-4xl font-black text-foreground mb-2 tracking-tight">
            MIKASA AI
          </h1>
          <p className="text-sm xl:text-base text-muted-foreground font-semibold mb-8 max-w-md">
            Your local sovereign AI assistant. How can I help you today?
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full">
            {quickActions.map((item) => (
              <button
                key={item.title}
                onClick={() => {
                  onSelectType?.(item.title);
                  onQuickAction?.(item.prompt);
                }}
                className="group p-4 rounded-2xl transition-all text-left flex flex-col gap-2 relative overflow-hidden border bg-accent/20 border-border/40 hover:bg-white dark:hover:bg-zinc-800 hover:border-orange-500/40 hover:shadow-lg active:scale-[0.99]"
              >
                <div className={`${item.color} p-0.5 flex items-center justify-between w-full`}>
                  <item.icon className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-xs xl:text-sm text-foreground mb-0.5 group-hover:text-orange-600 transition-colors">
                    {item.title}
                  </h3>
                  <p className="text-[11px] text-muted-foreground font-medium opacity-80 leading-relaxed">
                    {item.desc}
                  </p>
                </div>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="max-w-4xl mx-auto w-full flex flex-col gap-5 px-5 pb-36 pt-2">
          <AnimatePresence initial={false}>
            {messages.map((m, idx) => (
              <MessageBubble
                key={m.id || idx}
                message={m}
                isLast={idx === messages.length - 1}
                onRetry={onRetry}
              />
            ))}
          </AnimatePresence>

          {isStreaming &&
            messages.length > 0 &&
            messages[messages.length - 1].role === "assistant" &&
            !messages[messages.length - 1].content && <Loader />}
        </div>
      )}

      {/* Floating Scroll to Bottom Button */}
      {showScrollBottom && (
        <button
          onClick={() => scrollToBottom("smooth")}
          className="fixed bottom-24 right-8 p-2.5 bg-white dark:bg-zinc-800 border border-border shadow-xl rounded-full text-muted-foreground hover:text-foreground hover:scale-110 transition-all z-30"
          title="Scroll to bottom"
        >
          <ChevronDown className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
