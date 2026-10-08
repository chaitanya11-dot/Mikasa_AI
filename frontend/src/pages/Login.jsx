import React, { useState } from "react";
import { motion } from "framer-motion";
import { ShieldCheck, ArrowRight, User, Lock } from "lucide-react";

export default function Login({ onLogin }) {
  const [pilotId, setPilotId] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    // Simple mock logic: If any ID provided, let them in.
    if (pilotId.trim()) {
      onLogin();
    }
  };

  return (
    <div className="h-screen w-full flex items-center justify-center bg-white dark:bg-zinc-950 p-6">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md bg-white dark:bg-zinc-900 border border-border shadow-2xl rounded-[2.5rem] overflow-hidden p-8 xl:p-12 relative"
      >
        <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-orange-500 to-amber-500" />
        
        <div className="flex flex-col items-center text-center mb-10">
          <div className="w-20 h-20 bg-orange-600 rounded-3xl mb-6 flex items-center justify-center text-white shadow-xl shadow-orange-600/20">
            <img src="/logo.png" alt="Mikasa" className="w-12 h-12 object-contain brightness-0 invert" />
          </div>
          <h1 className="text-4xl font-black tracking-tighter mb-2">MIKASA CORE</h1>
          <p className="text-xs uppercase font-black tracking-widest text-muted-foreground/60 flex items-center gap-2">
            <ShieldCheck className="w-3 h-3 text-orange-500" />
            Security Authentication Required
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5 px-2">
            <label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/50 ml-1">Pilot Identity</label>
            <div className="relative">
              <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input 
                type="text" 
                placeholder="Enter Pilot ID (e.g. #7712)"
                value={pilotId}
                onChange={(e) => setPilotId(e.target.value)}
                className="w-full h-14 pl-12 pr-4 bg-accent/30 border border-border/50 rounded-2xl focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500/50 transition-all font-semibold"
              />
            </div>
          </div>

          <div className="space-y-1.5 px-2">
            <label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/50 ml-1">Access Protocol</label>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input 
                type="password" 
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full h-14 pl-12 pr-4 bg-accent/30 border border-border/50 rounded-2xl focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500/50 transition-all font-semibold"
              />
            </div>
          </div>

          <button 
            type="submit"
            className="w-full h-16 bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 rounded-3xl font-black text-lg shadow-xl shadow-orange-600/10 hover:scale-[1.02] active:scale-95 transition-all flex items-center justify-center gap-3 mt-8 group"
          >
            Authenticate Session
            <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
          </button>
        </form>

        <div className="mt-12 pt-8 border-t border-border/50 text-center">
          <p className="text-[9px] text-muted-foreground font-black uppercase tracking-[0.3em] opacity-40">
            Mikasa Cross-Platform Core v2.4.0
          </p>
        </div>
      </motion.div>
    </div>
  );
}
