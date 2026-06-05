"use client";

import { useState, useEffect } from "react";

const STORAGE_KEY = "adxray_api_key";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ApiKeyGateProps {
  onKeySet: (key: string) => void;
}

export default function ApiKeyGate({ onKeySet }: ApiKeyGateProps) {
  const [key, setKey] = useState("");
  const [remember, setRemember] = useState(true);
  const [validating, setValidating] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      setKey(saved);
      setRemember(true);
      validateAndProceed(saved);
    }
  }, []);

  async function validateAndProceed(apiKey: string) {
    setValidating(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/api/validate-key`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: apiKey }),
      });
      const data = await res.json();
      if (res.ok && data.valid) {
        if (remember) localStorage.setItem(STORAGE_KEY, apiKey);
        onKeySet(apiKey);
      } else {
        localStorage.removeItem(STORAGE_KEY);
        setError(data.detail || "Invalid API key. Get one at console.videodb.io");
      }
    } catch {
      setError("Could not reach the server. Make sure the backend is running.");
    } finally {
      setValidating(false);
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (key.trim()) validateAndProceed(key.trim());
  }

  return (
    <main className="flex-1 flex items-center justify-center px-6 min-h-screen">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl sm:text-5xl font-light tracking-tight text-foreground leading-[1.1] mb-4">
            Ad-<span className="text-primary">Xray</span>
          </h1>
          <p className="text-text-muted text-sm leading-relaxed">
            To use Ad-Xray, you need a free VideoDB API key.
            <br />
            <a
              href="https://console.videodb.io"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              Get one at console.videodb.io
            </a>
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="apikey" className="block text-xs font-mono text-text-subtle uppercase tracking-wider mb-2">
              VideoDB API Key
            </label>
            <input
              id="apikey"
              type="password"
              value={key}
              onChange={(e) => setKey(e.target.value)}
              placeholder="sk-..."
              disabled={validating}
              autoFocus
              className="w-full h-14 px-6 rounded-full bg-surface border border-border text-white
                placeholder:text-text-subtle text-base font-mono
                focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all duration-200"
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="remember"
              checked={remember}
              onChange={(e) => setRemember(e.target.checked)}
              className="rounded border-border bg-surface text-primary focus:ring-primary/20"
            />
            <label htmlFor="remember" className="text-xs text-text-subtle cursor-pointer select-none">
              Remember on this device
            </label>
          </div>

          {error && (
            <p className="text-sm text-danger text-center">{error}</p>
          )}

          <button
            type="submit"
            disabled={validating || !key.trim()}
            className="w-full h-14 rounded-full bg-primary text-white font-medium text-base
              hover:opacity-90 active:scale-[0.98]
              disabled:opacity-40 disabled:cursor-not-allowed disabled:active:scale-100
              transition-all duration-200 cursor-pointer select-none"
          >
            {validating ? "Validating..." : "Unlock Ad-Xray"}
          </button>
        </form>
      </div>
    </main>
  );
}
