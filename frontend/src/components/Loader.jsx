import React from 'react';

export default function Loader() {
  return (
    <div className="self-start flex items-center gap-1.5 px-6 py-4 bg-accent/50 rounded-3xl animate-pulse">
      <div className="w-1.5 h-1.5 bg-muted-foreground rounded-full animate-bounce [animation-delay:-0.3s]" />
      <div className="w-1.5 h-1.5 bg-muted-foreground rounded-full animate-bounce [animation-delay:-0.15s]" />
      <div className="w-1.5 h-1.5 bg-muted-foreground rounded-full animate-bounce" />
    </div>
  );
}
