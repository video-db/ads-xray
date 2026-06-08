"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import URLInput from "./components/URLInput";
import ApiKeyGate from "./components/ApiKeyGate";
import HistoryCard from "./components/HistoryCard";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getStoredKey(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("adxray_api_key");
}

export interface HistoryRun {
  job_id: string;
  video_name: string;
  status: string;
  progress: string;
  manipulation_score: number;
  primary_technique: string;
  duration: number;
  error: string;
  youtube_url: string;
  created_at: string;
}

export default function Home() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState<HistoryRun[]>([]);

  useEffect(() => {
    setMounted(true);
    const stored = getStoredKey();
    setApiKey(stored);
  }, []);

  useEffect(() => {
    if (!apiKey || !mounted) return;
    fetch(`${API_URL}/api/history?per_page=10`, {
      headers: { "X-VideoDB-Key": apiKey },
    })
      .then((r) => r.json())
      .then((data) => setHistory(data.runs || []))
      .catch(() => {});
  }, [apiKey, mounted]);

  useEffect(() => {
    const hasProcessing = history.some((r) => r.status === "processing");
    if (!hasProcessing) return;
    const interval = setInterval(() => {
      fetch(`${API_URL}/api/history?per_page=10`, {
        headers: { "X-VideoDB-Key": apiKey! },
      })
        .then((r) => r.json())
        .then((data) => setHistory(data.runs || []))
        .catch(() => {});
    }, 3000);
    return () => clearInterval(interval);
  }, [history, apiKey]);

  function handleKeySet(key: string) {
    localStorage.setItem("adxray_api_key", key);
    setApiKey(key);
  }

  function handleKeyClear() {
    localStorage.removeItem("adxray_api_key");
    setApiKey(null);
    setHistory([]);
  }

  if (!mounted) return null;

  if (!apiKey) {
    return <ApiKeyGate onKeySet={handleKeySet} />;
  }

  const handleSubmit = async (url: string, videoId?: string) => {
    setSubmitting(true);
    setError("");

    try {
      const body: Record<string, string | boolean> = { youtube_url: url };
      if (videoId) {
        body.video_id = videoId;
        body.force_fresh = true;
      }

      const res = await fetch(`${API_URL}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-VideoDB-Key": apiKey },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Failed to submit ad for analysis");
      }

      const { job_id } = await res.json();
      router.push(`/result/${job_id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
      setSubmitting(false);
    }
  };

  return (
    <main className="flex-1 flex flex-col">
      <section className="flex-1 flex flex-col items-center justify-center px-6 py-16 sm:py-24 min-h-screen">
        <div className="text-center max-w-3xl mb-8 sm:mb-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface border border-border mb-8">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            <span className="text-xs font-mono text-text-muted uppercase tracking-widest">
              AI-Powered Ad Deconstruction
            </span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-7xl font-light tracking-tight text-foreground leading-[1.1]">
            See Through the
            <br />
            <span className="text-primary">Persuasion Machine</span>
          </h1>
        </div>

        <URLInput onSubmit={handleSubmit} disabled={submitting} />

        {error && (
          <p className="mt-4 text-sm text-danger">{error}</p>
        )}

        {history.length > 0 && (
          <div className="w-full max-w-xl mx-auto mt-12">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-mono text-text-subtle uppercase tracking-widest">
                Recent Analyses
              </h3>
              <button
                onClick={() => router.push("/history")}
                className="text-xs text-primary hover:underline cursor-pointer"
              >
                View History →
              </button>
            </div>
            <div className="space-y-1.5">
              {history.filter((r) => r.status === "processing").map((run) => (
                <HistoryCard key={run.job_id} run={run} onClick={() => router.push(`/result/${run.job_id}`)} />
              ))}
              {history.filter((r) => r.status === "completed").slice(0, 4).map((run) => (
                <HistoryCard key={run.job_id} run={run} onClick={() => router.push(`/result/${run.job_id}`)} />
              ))}
              {history.filter((r) => r.status === "failed").slice(0, 2).map((run) => (
                <div key={run.job_id} className="flex items-center gap-3 px-4 py-3 rounded-card bg-surface border border-border">
                  <span className="w-2 h-2 rounded-full bg-danger flex-shrink-0" />
                  <span className="text-sm text-text-muted truncate flex-1">
                    {run.video_name || "Unknown"} — {run.error || "Failed"}
                  </span>
                  {run.youtube_url && (
                    <button
                      onClick={() => handleSubmit(run.youtube_url)}
                      className="text-xs text-primary hover:underline cursor-pointer flex-shrink-0"
                    >
                      Retry
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      <footer className="border-t border-border py-8 px-6">
        <div className="max-w-5xl mx-auto flex items-center justify-between gap-4">
          <span className="text-sm font-mono text-primary uppercase tracking-widest">Ad-Xray</span>
          <button
            onClick={handleKeyClear}
            className="text-xs text-text-subtle hover:text-danger transition-colors cursor-pointer"
          >
            Change API Key
          </button>
        </div>
      </footer>
    </main>
  );
}
