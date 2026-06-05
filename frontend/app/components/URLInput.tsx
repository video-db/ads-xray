"use client";

import { useState, useCallback } from "react";

interface URLInputProps {
  onSubmit: (url: string, videoId?: string) => void;
  disabled?: boolean;
}

export default function URLInput({ onSubmit, disabled }: URLInputProps) {
  const [url, setUrl] = useState("");
  const [testMode, setTestMode] = useState(false);

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      const trimmed = url.trim();
      if (trimmed) {
        if (testMode) {
          onSubmit("", trimmed);
        } else {
          onSubmit(trimmed);
        }
      }
    },
    [url, testMode, onSubmit],
  );

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="flex items-center gap-2 mb-4 justify-center">
        <button
          type="button"
          onClick={() => { setTestMode(false); setUrl(""); }}
          className={`text-xs font-mono px-3 py-1 rounded-full border transition-all duration-200 cursor-pointer ${
            !testMode
              ? "bg-primary/10 border-primary text-primary"
              : "border-border text-text-subtle hover:border-primary/30"
          }`}
        >
          YouTube URL
        </button>
        <button
          type="button"
          onClick={() => { setTestMode(true); setUrl(""); }}
          className={`text-xs font-mono px-3 py-1 rounded-full border transition-all duration-200 cursor-pointer ${
            testMode
              ? "bg-warning/10 border-warning text-warning"
              : "border-border text-text-subtle hover:border-warning/30"
          }`}
        >
          Video ID (Test)
        </button>
      </div>

      <div className="flex gap-3">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder={
            testMode
              ? "Paste VideoDB video ID... e.g. m-z-019e9823-..."
              : "Paste a YouTube ad URL... e.g. https://www.youtube.com/watch?v=..."
          }
          disabled={disabled}
          required
          className="flex-1 h-14 px-6 rounded-full bg-surface border border-border text-white
            placeholder:text-text-subtle text-base font-sans
            focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-all duration-200"
        />
        <button
          type="submit"
          disabled={disabled || !url.trim()}
          className={`h-14 px-8 rounded-full text-white font-medium text-base
            hover:opacity-90 active:scale-[0.98]
            disabled:opacity-40 disabled:cursor-not-allowed disabled:active:scale-100
            transition-all duration-200 cursor-pointer select-none whitespace-nowrap
            ${testMode ? "bg-warning" : "bg-primary hover:bg-primary-hover"}`}
        >
          {testMode ? "Test Run" : "X-Ray This Ad"}
        </button>
      </div>

      {testMode && (
        <p className="text-xs text-text-subtle mt-3 text-center">
          Test mode — skips YouTube upload and uses an existing VideoDB video directly.
        </p>
      )}
    </form>
  );
}
