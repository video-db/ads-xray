"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import ProgressTracker from "@/app/components/ProgressTracker";
import VideoPlayer from "@/app/components/VideoPlayer";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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
  narrative?: Narrative | null;
  error?: string;
}

export default function ResultPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const [data, setData] = useState<JobResult | null>(null);
  const [error, setError] = useState("");

  const poll = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/status/${jobId}`);
      if (!res.ok) {
        setError("Job not found");
        return;
      }
      const status = await res.json();

      if (status.status === "completed" || status.status === "failed") {
        const finalRes = await fetch(`${API_URL}/api/result/${jobId}`);
        if (finalRes.ok) {
          setData(await finalRes.json());
        } else {
          setData({ job_id: jobId as string, status: status.status, error: status.error });
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
        </div>
      </main>
    );
  }

  if (!data) {
    return (
      <main className="flex-1 flex items-center justify-center px-6">
        <div className="w-12 h-12 rounded-full border-2 border-primary border-t-transparent animate-spin" />
      </main>
    );
  }

  return (
    <main className="flex-1 flex flex-col px-6 py-12">
      <div className="max-w-5xl mx-auto w-full">
        <ProgressTracker
          status={data.status as "pending" | "processing" | "completed" | "failed"}
          progress={data.status === "completed" ? "done" : data.status === "failed" ? "error" : "processing"}
          error={data.error}
        />

        {data.status === "completed" && data.stream_url && (
          <VideoPlayer
            streamUrl={data.stream_url}
            scenes={data.scenes}
            breakdown={data.breakdown}
            primaryTechnique={data.primary_technique}
            emotionalTriggers={data.emotional_triggers}
            cognitiveBiases={data.cognitive_biases}
            adArchetype={data.ad_archetype}
            targetAudience={data.target_audience}
            narrative={data.narrative}
            videoName={data.video_name}
            youtubeUrl={data.youtube_url}
            duration={data.duration}
          />
        )}
      </div>
    </main>
  );
}
