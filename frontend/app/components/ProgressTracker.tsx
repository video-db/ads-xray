"use client";

interface ProgressTrackerProps {
  progress: string;
}

const STAGES: Record<string, string> = {
  queued: "Initializing...",
  uploading: "Uploading video...",
  loading_video: "Loading video...",
  indexing_shots: "Analyzing scene-by-scene...",
  synthesizing_report: "Synthesizing psychological insights...",
  analyzing_audio: "Analyzing spoken words...",
  storing_results: "Compiling report...",
  generating_defense: "Building defense strategies...",
  rendering_video: "Rendering annotated video...",
};

function getCurrentIndex(progress: string): number {
  const keys = Object.keys(STAGES);
  const idx = keys.indexOf(progress);
  return idx >= 0 ? idx : 0;
}

export default function ProgressTracker({ progress }: ProgressTrackerProps) {
  const currentIdx = getCurrentIndex(progress);
  const keys = Object.keys(STAGES);
  const label = STAGES[progress] || progress;

  return (
    <div className="w-full max-w-md mx-auto py-16 text-center">
      <div className="inline-flex items-center gap-3 mb-8">
        <div className="w-3 h-3 rounded-full bg-primary animate-pulse" />
        <span className="text-sm text-text-muted font-sans">{label}</span>
      </div>

      <div className="flex items-center justify-center gap-1.5 flex-wrap">
        {keys.map((key, idx) => {
          const isDone = idx < currentIdx;
          const isCurrent = idx === currentIdx;
          return (
            <div
              key={key}
              className={`w-2 h-2 rounded-full transition-all duration-500 ${
                isDone
                  ? "bg-success/60"
                  : isCurrent
                    ? "bg-primary"
                    : "bg-border"
              }`}
              title={STAGES[key]}
            />
          );
        })}
      </div>

      <p className="text-xs text-text-subtle mt-6 font-mono">
        Step {currentIdx + 1} of {keys.length}
      </p>
    </div>
  );
}
