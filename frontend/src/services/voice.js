// Speech Synthesis & Recognition Service for MIKASA

let currentRecognition = null;
let currentUtterance = null;

export const voiceManager = {
  isSpeechRecognitionSupported() {
    return typeof window !== "undefined" && ("SpeechRecognition" in window || "webkitSpeechRecognition" in window);
  },

  isSpeechSynthesisSupported() {
    return typeof window !== "undefined" && "speechSynthesis" in window;
  },

  startListening({ onResult, onError, onEnd }) {
    if (!this.isSpeechRecognitionSupported()) {
      onError?.(new Error("Speech recognition is not supported in this browser."));
      return null;
    }

    this.stopListening();

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      let interimTranscript = "";
      let finalTranscript = "";

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      onResult?.({
        text: finalTranscript || interimTranscript,
        isFinal: Boolean(finalTranscript)
      });
    };

    recognition.onerror = (event) => {
      console.warn("Speech recognition error:", event.error);
      onError?.(event);
    };

    recognition.onend = () => {
      currentRecognition = null;
      onEnd?.();
    };

    try {
      recognition.start();
      currentRecognition = recognition;
      return recognition;
    } catch (e) {
      console.error("Failed to start speech recognition:", e);
      onError?.(e);
      return null;
    }
  },

  stopListening() {
    if (currentRecognition) {
      try {
        currentRecognition.stop();
      } catch (e) {}
      currentRecognition = null;
    }
  },

  speak(text, { rate = 1.0, pitch = 1.0, volume = 1.0, onStart, onEnd, onError } = {}) {
    if (!this.isSpeechSynthesisSupported() || !text) return;

    this.stopSpeaking();

    // Clean markdown symbols for natural speech
    const cleanText = text
      .replace(/```[\s\S]*?```/g, "Code block omitted.")
      .replace(/`([^`]+)`/g, "$1")
      .replace(/[*_~#>-]/g, "")
      .replace(/\[([^\]]+)\]\([^\)]+\)/g, "$1")
      .trim();

    if (!cleanText) return;

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = Math.max(0.5, Math.min(2.0, rate));
    utterance.pitch = Math.max(0.5, Math.min(2.0, pitch));
    utterance.volume = Math.max(0.0, Math.min(1.0, volume));

    // Try finding natural sounding english voice
    const voices = window.speechSynthesis.getVoices();
    const naturalVoice = voices.find(
      (v) => (v.name.includes("Natural") || v.name.includes("Neural") || v.name.includes("Female") || v.name.includes("Google") || v.name.includes("Samantha")) && v.lang.startsWith("en")
    ) || voices.find((v) => v.lang.startsWith("en"));

    if (naturalVoice) {
      utterance.voice = naturalVoice;
    }

    utterance.onstart = () => {
      onStart?.();
    };

    utterance.onend = () => {
      currentUtterance = null;
      onEnd?.();
    };

    utterance.onerror = (e) => {
      console.warn("Speech synthesis error:", e);
      currentUtterance = null;
      onError?.(e);
    };

    currentUtterance = utterance;
    window.speechSynthesis.speak(utterance);
  },

  stopSpeaking() {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      currentUtterance = null;
    }
  },

  isSpeaking() {
    return typeof window !== "undefined" && "speechSynthesis" in window && window.speechSynthesis.speaking;
  }
};
