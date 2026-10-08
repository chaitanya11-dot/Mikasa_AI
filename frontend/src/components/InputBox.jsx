import React, { useRef, useState, useEffect } from "react";
import { ArrowUp, Mic, Square, MicOff } from "lucide-react";
import { voiceManager } from "@/services/voice";

export default function InputBox({ onSend, onStop, isStreaming, enterToSend = true }) {
  const inputRef = useRef(null);
  const [text, setText] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [voiceNotice, setVoiceNotice] = useState("");

  const handleSend = () => {
    if (isStreaming) {
      onStop?.();
      return;
    }
    const trimmed = text.trim();
    if (trimmed) {
      onSend(trimmed);
      setText("");
      if (inputRef.current) {
        inputRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e) => {
    if (enterToSend && e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextChange = (e) => {
    setText(e.target.value);
    // Auto-adjust height up to 160px
    e.target.style.height = "auto";
    e.target.style.height = `${Math.min(e.target.scrollHeight, 160)}px`;
  };

  const handleToggleVoiceInput = () => {
    if (isListening) {
      voiceManager.stopListening();
      setIsListening(false);
      setVoiceNotice("");
    } else {
      if (!voiceManager.isSpeechRecognitionSupported()) {
        setVoiceNotice("Speech recognition is not supported in this browser.");
        setTimeout(() => setVoiceNotice(""), 3500);
        return;
      }

      setIsListening(true);
      setVoiceNotice("Listening to speech...");

      voiceManager.startListening({
        onResult: ({ text: transcript, isFinal }) => {
          setText(transcript);
          if (isFinal) {
            setIsListening(false);
            setVoiceNotice("");
          }
        },
        onError: (err) => {
          console.warn("Speech error:", err);
          setIsListening(false);
          setVoiceNotice("Voice input stopped.");
          setTimeout(() => setVoiceNotice(""), 2500);
        },
        onEnd: () => {
          setIsListening(false);
          setVoiceNotice("");
        }
      });
    }
  };

  return (
    <div className="max-w-3xl mx-auto w-full relative group">
      {voiceNotice && (
        <div className="absolute -top-7 left-4 text-xs font-semibold text-orange-500 animate-pulse flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-orange-500 animate-ping" />
          {voiceNotice}
        </div>
      )}

      <div
        className={`bg-white dark:bg-zinc-900 border rounded-3xl p-1.5 flex items-end gap-2 pl-4 pr-2 shadow-sm focus-within:shadow-xl transition-all duration-200 ${
          isListening
            ? "border-orange-500 ring-2 ring-orange-500/20"
            : "border-border/80 focus-within:border-orange-500/60"
        }`}
      >
        {/* Voice Input Button */}
        <button
          type="button"
          onClick={handleToggleVoiceInput}
          className={`w-10 h-10 mb-0.5 rounded-2xl flex items-center justify-center transition-all ${
            isListening
              ? "bg-orange-600 text-white animate-pulse"
              : "text-muted-foreground hover:bg-accent hover:text-foreground"
          }`}
          title={isListening ? "Stop Listening" : "Speak to MIKASA"}
        >
          {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
        </button>

        {/* Text Input Area */}
        <textarea
          ref={inputRef}
          value={text}
          onChange={handleTextChange}
          onKeyDown={handleKeyDown}
          placeholder={isListening ? "Listening... Speak now." : "Ask MIKASA anything..."}
          rows={1}
          className="flex-1 bg-transparent border-none outline-none resize-none py-2.5 text-sm placeholder:text-muted-foreground font-medium max-h-40 custom-scrollbar"
        />

        {/* Send / Stop Button */}
        <button
          type="button"
          onClick={handleSend}
          disabled={!isStreaming && !text.trim()}
          className={`w-10 h-10 mb-0.5 rounded-2xl text-white flex items-center justify-center transition-all active:scale-95 disabled:opacity-30 shadow-md ${
            isStreaming
              ? "bg-red-500 hover:bg-red-600 shadow-red-500/20"
              : "bg-orange-600 hover:bg-orange-500 shadow-orange-600/20"
          }`}
          title={isStreaming ? "Stop Generating" : "Send Message"}
        >
          {isStreaming ? (
            <Square className="w-4 h-4 fill-white" />
          ) : (
            <ArrowUp className="w-4 h-4 stroke-[2.5px]" />
          )}
        </button>
      </div>
    </div>
  );
}
