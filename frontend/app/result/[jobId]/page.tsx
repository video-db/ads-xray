"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import VideoPlayer from "@/app/components/VideoPlayer";
import ProgressTracker from "@/app/components/ProgressTracker";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getApiKey(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("adxray_api_key");
}

interface SceneResult {
  start_time: number;
  end_time: number;
  overlay_text: string;
  description: string;
}

interface Narrative {
  strategy?: string;
  fears_exploited?: string[];
  desires_exploited?: string[];
  story_arc?: string;
  key_phrases?: { phrase: string; manipulation: string }[];
  voice_tone?: string;
}

interface JobResult {
  job_id: string;
  status: string;
  progress?: string;
  stream_url?: string;
  duration?: number;
  video_name?: string;
  youtube_url?: string;
  scenes?: SceneResult[];
  breakdown?: string;
  primary_technique?: string;
  emotional_triggers?: string[];
  cognitive_biases?: string[];
  ad_archetype?: string;
  target_audience?: string;
  symbols_exploited?: string[];
  narrative?: Narrative | null;
  manipulation_score?: number;
  defense_strategies?: { technique_targeted: string; strategy: string; question_to_ask: string }[];
  empowerment_message?: string;
  error?: string;
}

export default function ResultPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const [data, setData] = useState<JobResult | null>(null);
  const [error, setError] = useState("");

  const poll = useCallback(async () => {
    try {
      const apiKey = getApiKey() || "";
      const res = await fetch(`${API_URL}/api/status/${jobId}`, {
        headers: { "X-VideoDB-Key": apiKey },
      });
      if (!res.ok) {
        if (res.status === 429) return; // rate limited — retry next interval
        setError("Job not found");
        return;
      }
      const status = await res.json();

      if (status.status === "completed" || status.status === "failed") {
        try {
          const finalRes = await fetch(`${API_URL}/api/result/${jobId}`, {
            headers: { "X-VideoDB-Key": apiKey },
          });
          if (finalRes.ok) {
            setData(await finalRes.json());
          } else {
            setData({ job_id: jobId as string, status: status.status, error: status.error || "Analysis failed" });
          }
        } catch {
          setData({ job_id: jobId as string, status: status.status, error: status.error || "Unable to retrieve result" });
        }
      } else {
        setData({ job_id: jobId as string, status: status.status, progress: status.progress });
      }
    } catch (e) {
      setError("Failed to connect to backend");
    }
  }, [jobId]);

  useEffect(() => {
    poll();
    const interval = setInterval(() => {
      if (!data || (data.status !== "completed" && data.status !== "failed")) {
        poll();
      } else {
        clearInterval(interval);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [poll, data]);

  if (error) {
    return (
      <main className="flex-1 flex items-center justify-center px-6">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-danger/10 flex items-center justify-center">
            <svg className="w-8 h-8 text-danger" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="text-text-muted">{error}</p>
          <a href="/" className="text-xs text-primary hover:underline cursor-pointer mt-4 inline-block">← Back</a>
        </div>
      </main>
    );
  }

  if (!data) {
    return (
      <main className="flex-1 flex items-center justify-center px-6">
        <ProgressTracker progress="queued" />
      </main>
    );
  }

  if (data.status === "completed" && data.stream_url) {
    return (
      <main className="flex-1 flex flex-col px-6 py-6 sm:py-12">
        <div className="max-w-5xl mx-auto w-full">
          <VideoPlayer
            streamUrl={data.stream_url}
            scenes={data.scenes}
            breakdown={data.breakdown}
            primaryTechnique={data.primary_technique}
            emotionalTriggers={data.emotional_triggers}
            cognitiveBiases={data.cognitive_biases}
            adArchetype={data.ad_archetype}
            targetAudience={data.target_audience}
            symbolsExploited={data.symbols_exploited}
            narrative={data.narrative}
            videoName={data.video_name}
            youtubeUrl={data.youtube_url}
            duration={data.duration}
            manipulationScore={data.manipulation_score}
            defenseStrategies={data.defense_strategies}
            empowermentMessage={data.empowerment_message}
          />
        </div>
      </main>
    );
  }

  if (data.status === "failed") {
    const retryUrl = data.youtube_url || data.error?.match(/https?:\/\/[^\s]+/)?.[0] || "";
    return (
      <main className="flex-1 flex items-center justify-center px-6">
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-danger/10 flex items-center justify-center">
            <svg className="w-8 h-8 text-danger" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="text-xl font-light text-foreground mb-2">Analysis Failed</h2>
          <p className="text-text-muted mt-1">{data.error || "Something went wrong. Please try again."}</p>
          <div className="flex items-center justify-center gap-3 mt-6">
            <a href="/" className="text-xs text-text-subtle hover:text-foreground cursor-pointer">← Back</a>
            {retryUrl && (
              <button
                onClick={async () => {
                  const apiKey = getApiKey() || "";
                  try {
                    const res = await fetch(`${API_URL}/api/analyze`, {
                      method: "POST",
                      headers: { "Content-Type": "application/json", "X-VideoDB-Key": apiKey },
                      body: JSON.stringify({ youtube_url: retryUrl }),
                    });
                    if (res.ok) {
                      const { job_id } = await res.json();
                      window.location.href = `/result/${job_id}`;
                    } else {
                      const d = await res.json().catch(() => ({}));
                      setData({ job_id: jobId as string, status: "failed", error: d.detail || "Retry failed" });
                    }
                  } catch {
                    setData({ job_id: jobId as string, status: "failed", error: "Retry failed — backend unreachable" });
                  }
                }}
                className="text-xs px-4 py-2 rounded-full bg-primary text-white hover:bg-primary/90 transition-colors cursor-pointer"
              >
                Retry
              </button>
            )}
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="flex-1 flex flex-col items-center justify-center px-6 gap-6">
      <ProgressTracker progress={data.progress || "queued"} />
      <button
        onClick={() => window.location.href = "/"}
        className="text-xs text-text-subtle hover:text-foreground cursor-pointer transition-colors"
      >
        Run in Background →
      </button>
    </main>
  );
}
