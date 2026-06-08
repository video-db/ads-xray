"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import HistoryCard from "@/app/components/HistoryCard";
import type { HistoryRun } from "@/app/page";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const PER_PAGE = 10;

function getApiKey(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("adxray_api_key");
}

export default function HistoryPage() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [runs, setRuns] = useState<HistoryRun[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setMounted(true);
    setApiKey(getApiKey());
  }, []);

  useEffect(() => {
    if (!apiKey || !mounted) return;
    setLoading(true);
    fetch(`${API_URL}/api/history?page=${page}&per_page=${PER_PAGE}`, {
      headers: { "X-VideoDB-Key": apiKey },
    })
      .then((r) => r.json())
      .then((data) => {
        setRuns(data.runs || []);
        setTotalPages(data.total_pages || 1);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [apiKey, mounted, page]);

  useEffect(() => {
    const hasProcessing = runs.some((r) => r.status === "processing");
    if (!hasProcessing) return;
    const interval = setInterval(() => {
      fetch(`${API_URL}/api/history?page=${page}&per_page=${PER_PAGE}`, {
        headers: { "X-VideoDB-Key": apiKey! },
      })
        .then((r) => r.json())
        .then((data) => {
          setRuns(data.runs || []);
          setTotalPages(data.total_pages || 1);
        })
        .catch(() => {});
    }, 3000);
    return () => clearInterval(interval);
  }, [runs, page, apiKey]);

  if (!mounted) return null;

  if (!apiKey) {
    return (
      <main className="flex-1 flex items-center justify-center px-6">
        <p className="text-text-muted text-sm">
          <button onClick={() => router.push("/")} className="text-primary hover:underline cursor-pointer">
            Go back
          </button>{" "}
          and log in to view your history.
        </p>
      </main>
    );
  }

  return (
    <main className="flex-1 flex flex-col px-6 py-8 sm:py-12">
      <div className="max-w-xl mx-auto w-full">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-xl font-light text-foreground">Analysis History</h1>
            <p className="text-xs text-text-subtle mt-1">All your past X-rays</p>
          </div>
          <button
            onClick={() => router.push("/")}
            className="text-xs text-primary hover:underline cursor-pointer"
          >
            ← New X-Ray
          </button>
        </div>

        {loading ? (
          <p className="text-sm text-text-subtle text-center py-8">Loading...</p>
        ) : runs.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-text-muted text-sm mb-4">No analyses yet.</p>
            <button
              onClick={() => router.push("/")}
              className="text-sm text-primary hover:underline cursor-pointer"
            >
              X-Ray your first ad
            </button>
          </div>
        ) : (
          <>
            <div className="space-y-1.5">
              {runs
                .filter((r) => r.status === "completed" || r.status === "failed" || r.status === "processing")
                .map((run) => (
                  <div key={run.job_id} className="flex items-center gap-3">
                    <HistoryCard
                      run={run}
                      onClick={() => {
                        if (run.status === "completed" || run.status === "processing") {
                          router.push(`/result/${run.job_id}`);
                        }
                      }}
                    />
                    {run.status === "failed" && run.youtube_url && (
                      <button
                        onClick={async () => {
                          const key = getApiKey() || "";
                          try {
                            const res = await fetch(`${API_URL}/api/analyze`, {
                              method: "POST",
                              headers: { "Content-Type": "application/json", "X-VideoDB-Key": key },
                              body: JSON.stringify({ youtube_url: run.youtube_url }),
                            });
                            if (res.ok) {
                              const { job_id } = await res.json();
                              router.push(`/result/${job_id}`);
                            }
                          } catch {}
                        }}
                        className="text-xs text-primary hover:underline cursor-pointer flex-shrink-0 ml-2"
                      >
                        Retry
                      </button>
                    )}
                  </div>
                ))}
            </div>

            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-4 mt-8">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  className="text-xs text-text-subtle hover:text-foreground disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer transition-colors"
                >
                  ← Previous
                </button>
                <span className="text-xs text-text-muted font-mono">
                  {page} / {totalPages}
                </span>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                  className="text-xs text-text-subtle hover:text-foreground disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer transition-colors"
                >
                  Next →
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}
