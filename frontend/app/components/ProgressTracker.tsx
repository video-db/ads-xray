"use client";

interface ProgressTrackerProps {
  progress: string;
}

const STAGES = [
  { key: "queued", label: "Queued" },
  { key: "uploading", label: "Upload" },
  { key: "indexing_shots", label: "Analyze" },
  { key: "synthesizing_report", label: "Synthesize" },
  { key: "analyzing_audio", label: "Audio" },
  { key: "generating_defense", label: "Defense" },
  { key: "rendering_video", label: "Render" },
];

const STAGE_INDEX: Record<string, number> = {
  queued: 0,
  uploading: 1,
  loading_video: 1,
  indexing_shots: 2,
  synthesizing_report: 3,
  storing_results: 3,
  analyzing_audio: 4,
  generating_defense: 5,
  rendering_video: 6,
  done: 6,
};

const STATUS_LABELS: Record<string, string> = {
  queued: "Preparing analysis...",
  uploading: "Uploading video...",
  loading_video: "Loading video...",
  indexing_shots: "Analyzing scene-by-scene...",
  synthesizing_report: "Synthesizing psychological insights...",
  analyzing_audio: "Analyzing spoken words...",
  storing_results: "Compiling report...",
  generating_defense: "Building defense strategies...",
  rendering_video: "Rendering annotated video...",
  done: "Complete",
};

export default function ProgressTracker({ progress }: ProgressTrackerProps) {
  const currentIdx = STAGE_INDEX[progress] ?? 0;
  const statusLabel = STATUS_LABELS[progress] || progress;
  const total = STAGES.length - 1;

  return (
    <div className="w-full max-w-2xl mx-auto py-8 sm:py-14 px-4">
      <h2 className="text-lg sm:text-xl font-light text-center text-foreground mb-1">Analyzing Your Ad</h2>
      <p className="text-xs text-text-subtle text-center mb-8">We're exposing the hidden psychology...</p>
      <div className="flex items-center gap-3 mb-8 justify-center">
        <div className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse flex-shrink-0" />
        <span className="text-sm text-text-muted">{statusLabel}</span>
      </div>

      <div className="relative pt-3">
        <div className="absolute top-[19px] left-0 right-0 h-px bg-border" />

        <div
          className="absolute top-[19px] left-0 h-px bg-primary transition-all duration-700 ease-out"
          style={{ width: `${total > 0 ? (currentIdx / total) * 100 : 0}%` }}
        />

        <div className="relative flex justify-between">
          {STAGES.map((stage, idx) => {
            const isDone = idx < currentIdx;
            const isCurrent = idx === currentIdx;
            const isPending = idx > currentIdx;

            return (
              <div key={stage.key} className="flex flex-col items-center gap-2.5">
                <div className="relative flex items-center justify-center h-8">
                  {isCurrent ? (
                    <>
                      <div className="absolute w-6 h-6 rounded-full bg-primary/20 animate-ping" />
                      <div className="w-3.5 h-3.5 rounded-full bg-primary ring-2 ring-primary/30" />
                    </>
                  ) : isDone ? (
                    <div className="w-3 h-3 rounded-full bg-primary">
                      <svg className="w-full h-full" viewBox="0 0 12 12" fill="none">
                        <path d="M2.5 6.5L4.5 8.5L9.5 3.5" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </div>
                  ) : (
                    <div className="w-3 h-3 rounded-full bg-border" />
                  )}
                </div>
                <span
                  className={`text-[10px] font-mono uppercase tracking-wider whitespace-nowrap transition-colors duration-300 hidden sm:block ${
                    isCurrent
                      ? "text-primary"
                      : isDone
                        ? "text-text-muted"
                        : "text-text-subtle"
                  }`}
                >
                  {stage.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
