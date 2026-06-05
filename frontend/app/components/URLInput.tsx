import { useState, useCallback } from "react";

interface URLInputProps {
  onSubmit: (url: string) => void;
  disabled?: boolean;
}

export default function URLInput({ onSubmit, disabled }: URLInputProps) {
  const [url, setUrl] = useState("");

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      const trimmed = url.trim();
      if (trimmed) onSubmit(trimmed);
    },
    [url, onSubmit],
  );

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="flex gap-3">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Paste a YouTube ad URL... e.g. https://www.youtube.com/watch?v=..."
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
          className="h-14 px-8 rounded-full bg-primary text-white font-medium text-base
            hover:bg-primary-hover active:scale-[0.98]
            disabled:opacity-40 disabled:cursor-not-allowed disabled:active:scale-100
            transition-all duration-200 cursor-pointer select-none whitespace-nowrap"
        >
          X-Ray This Ad
        </button>
      </div>
    </form>
  );
}
