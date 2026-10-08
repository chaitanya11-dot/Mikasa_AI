import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Copy, Check, Volume2, Square, RotateCcw } from "lucide-react";
import { voiceManager } from "@/services/voice";

const CodeBlock = ({ children, className }) => {
  const [isCopied, setIsCopied] = useState(false);
  const language = (className || "").replace("language-", "") || "code";

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(String(children).trim());
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy!", err);
    }
  };

  return (
    <div className="my-3 rounded-2xl overflow-hidden border border-zinc-800 shadow-xl bg-zinc-950">
      <div className="flex items-center justify-between bg-zinc-900/80 px-4 py-2 border-b border-zinc-800">
        <span className="text-[10px] text-zinc-400 font-mono font-bold uppercase tracking-wider">
          {language}
        </span>
        <div className="flex items-center gap-3">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 text-zinc-400 hover:text-white transition-colors group text-xs font-semibold"
          >
            <AnimatePresence mode="wait">
              {isCopied ? (
                <motion.div
                  key="check"
                  initial={{ scale: 0.5, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.5, opacity: 0 }}
                  className="flex items-center gap-1 text-green-400"
                >
                  <Check className="w-3.5 h-3.5" />
                  <span className="text-[10px] uppercase font-bold">Copied</span>
                </motion.div>
              ) : (
                <motion.div
                  key="copy"
                  initial={{ scale: 0.5, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.5, opacity: 0 }}
                  className="flex items-center gap-1"
                >
                  <Copy className="w-3.5 h-3.5 group-hover:scale-110 transition-transform" />
                  <span className="text-[10px] uppercase font-bold">Copy</span>
                </motion.div>
              )}
            </AnimatePresence>
          </button>
          <div className="flex gap-1.5 ml-2 border-l border-zinc-800 pl-3">
            <span className="w-2 h-2 rounded-full bg-red-500/60" />
            <span className="w-2 h-2 rounded-full bg-yellow-500/60" />
            <span className="w-2 h-2 rounded-full bg-green-500/60" />
          </div>
        </div>
      </div>
      <pre className="bg-zinc-950 text-emerald-400 p-4 overflow-x-auto text-xs font-mono leading-relaxed whitespace-pre custom-scrollbar">
        <code>{children}</code>
      </pre>
    </div>
  );
};

export default function MessageBubble({ message, isLast, onRetry }) {
  const isAI = message.role === "assistant";
  const [isCopied, setIsCopied] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const handleCopyMessage = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (e) {
      console.error("Failed to copy message:", e);
    }
  };

  const handleToggleSpeak = () => {
    if (isSpeaking) {
      voiceManager.stopSpeaking();
      setIsSpeaking(false);
    } else {
      setIsSpeaking(true);
      voiceManager.speak(message.content, {
        onEnd: () => setIsSpeaking(false),
        onError: () => setIsSpeaking(false)
      });
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex w-full ${isAI ? "justify-start" : "justify-end"}`}
    >
      <div
        className={`text-sm leading-relaxed min-w-0 ${
          isAI
            ? "text-foreground w-full max-w-[90%]"
            : "bg-orange-600 text-white rounded-3xl rounded-tr-sm px-5 py-3 font-medium max-w-[70%] break-words shadow-sm"
        }`}
      >
        {isAI ? (
          <div className="space-y-2">
            {/* AI Header Label */}
            <div className="flex items-center justify-between px-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-black uppercase tracking-wider text-orange-600 dark:text-orange-500">
                  MIKASA
                </span>
              </div>
            </div>

            {/* Bubble Content */}
            <div className="bg-accent/40 border border-border/70 rounded-3xl rounded-tl-sm px-6 py-4 space-y-3 shadow-sm">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  p: ({ children }) => (
                    <p className="mb-2.5 last:mb-0 break-words text-foreground/90 leading-7 font-normal">
                      {children}
                    </p>
                  ),
                  ul: ({ children }) => (
                    <ul className="list-none mb-3 space-y-1.5 pl-1">{children}</ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="list-decimal list-inside mb-3 space-y-1.5 pl-1">{children}</ol>
                  ),
                  li: ({ children }) => (
                    <li className="flex gap-2 leading-relaxed text-foreground/90">
                      <span className="text-orange-500 font-bold shrink-0 mt-0.5">•</span>
                      <span className="break-words">{children}</span>
                    </li>
                  ),
                  strong: ({ children }) => (
                    <strong className="font-bold text-foreground">{children}</strong>
                  ),
                  em: ({ children }) => (
                    <em className="italic text-foreground/85">{children}</em>
                  ),
                  code: ({ inline, className, children }) =>
                    inline ? (
                      <code className="bg-accent text-orange-600 dark:text-orange-400 px-1.5 py-0.5 rounded-md text-[0.85em] font-mono border border-border">
                        {children}
                      </code>
                    ) : (
                      <CodeBlock className={className}>{children}</CodeBlock>
                    ),
                  a: ({ children, href }) => (
                    <a
                      href={href}
                      className="text-orange-600 dark:text-orange-400 underline underline-offset-2 hover:opacity-80 break-all"
                      target="_blank"
                      rel="noreferrer"
                    >
                      {children}
                    </a>
                  ),
                  h1: ({ children }) => (
                    <h1 className="text-2xl font-black mb-3 mt-2 text-foreground tracking-tight">
                      {children}
                    </h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className="text-xl font-bold mb-2.5 mt-2 text-foreground tracking-tight">
                      {children}
                    </h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="text-base font-bold mb-2 mt-1.5 text-foreground">
                      {children}
                    </h3>
                  ),
                  blockquote: ({ children }) => (
                    <blockquote className="border-l-4 border-orange-500 pl-4 my-3 italic text-muted-foreground bg-accent/20 py-2 rounded-r-xl">
                      {children}
                    </blockquote>
                  ),
                  hr: () => <hr className="border-border my-4" />,
                  table: ({ children }) => (
                    <div className="overflow-x-auto my-3 rounded-xl border border-border">
                      <table className="w-full text-xs border-collapse">{children}</table>
                    </div>
                  ),
                  th: ({ children }) => (
                    <th className="border-b border-border bg-accent/70 px-4 py-2.5 text-left font-bold text-foreground">
                      {children}
                    </th>
                  ),
                  td: ({ children }) => (
                    <td className="border-b border-border/50 px-4 py-2 text-foreground/90">
                      {children}
                    </td>
                  )
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>

            {/* AI Message Action Toolbar */}
            {message.content && (
              <div className="flex items-center gap-2 px-2 pt-1 text-muted-foreground">
                <button
                  onClick={handleCopyMessage}
                  className="flex items-center gap-1 px-2 py-1 rounded-lg text-xs hover:bg-accent hover:text-foreground transition-all"
                  title="Copy response"
                >
                  {isCopied ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-green-500" />
                      <span className="text-[10px] font-bold text-green-500">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span className="text-[10px] font-semibold">Copy</span>
                    </>
                  )}
                </button>

                <button
                  onClick={handleToggleSpeak}
                  className={`flex items-center gap-1 px-2 py-1 rounded-lg text-xs hover:bg-accent transition-all ${
                    isSpeaking ? "text-orange-500 font-bold" : "hover:text-foreground"
                  }`}
                  title={isSpeaking ? "Stop Speaking" : "Read aloud"}
                >
                  {isSpeaking ? <Square className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5" />}
                  <span className="text-[10px] font-semibold">
                    {isSpeaking ? "Stop" : "Speak"}
                  </span>
                </button>

                {isLast && onRetry && (
                  <button
                    onClick={onRetry}
                    className="flex items-center gap-1 px-2 py-1 rounded-lg text-xs hover:bg-accent hover:text-foreground transition-all"
                    title="Regenerate response"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span className="text-[10px] font-semibold">Retry</span>
                  </button>
                )}
              </div>
            )}
          </div>
        ) : (
          <span className="break-words leading-relaxed">{message.content}</span>
        )}
      </div>
    </motion.div>
  );
}
