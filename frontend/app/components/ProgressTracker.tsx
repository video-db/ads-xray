interface SceneResult {
  start_time: number;
  end_time: number;
  overlay_text: string;
  description: string;
}

interface ProgressTrackerProps {
  status: "pending" | "processing" | "completed" | "failed";
  progress: string;
  error?: string;
  scenes?: SceneResult[];
}

const progressStages = [
  { key: "queued", label: "Queued" },
  { key: "uploading", label: "Uploading video" },
  { key: "analyzing_scenes", label: "Analyzing scenes with AI" },
  { key: "generating_commentary", label: "Generating commentary" },
  { key: "rendering_video", label: "Rendering annotated video" },
  { key: "done", label: "Complete" },
];

export default function ProgressTracker({
  status,
  progress,
  error,
}: ProgressTrackerProps) {
  const currentIdx = progressStages.findIndex((s) => s.key === progress);

  return (
    <div className="w-full max-w-2xl mx-auto py-16">
      {status === "failed" ? (
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-danger/10 flex items-center justify-center">
            <svg className="w-8 h-8 text-danger" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="text-2xl font-light text-foreground mb-2">Analysis Failed</h2>
          <p className="text-text-muted">{error || "Something went wrong."}</p>
        </div>
      ) : status === "completed" ? (
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-success/10 flex items-center justify-center">
            <svg className="w-8 h-8 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-2xl font-light text-foreground mb-2">X-Ray Complete</h2>
          <p className="text-text-muted">Scroll down to watch the annotated ad.</p>
        </div>
      ) : (
        <div className="space-y-5">
          <div className="text-center mb-8">
            <div className="inline-block w-12 h-12 rounded-full border-2 border-primary border-t-transparent animate-spin mb-4" />
            <h2 className="text-2xl font-light text-foreground">Analyzing Your Ad</h2>
            <p className="text-text-muted mt-1">We&apos;re exposing the hidden psychology...</p>
          </div>
          <div className="space-y-2">
            {progressStages.map((stage, idx) => {
              const isComplete = idx < currentIdx;
              const isCurrent = idx === currentIdx;
              const isPending = idx > currentIdx;

              return (
                <div
                  key={stage.key}
                  className={`flex items-center gap-3 px-4 py-3 rounded-card transition-all duration-300 ${
                    isCurrent ? "bg-surface border border-primary/30" : ""
                  }`}
                >
                  <div
                    className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 transition-all ${
                      isComplete
                        ? "bg-success"
                        : isCurrent
                          ? "bg-primary animate-pulse"
                          : "bg-surface border border-border"
                    }`}
                  >
                    {isComplete && (
                      <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                  </div>
                  <span
                    className={`text-sm transition-colors ${
                      isComplete ? "text-text-muted" : isCurrent ? "text-foreground font-medium" : "text-text-subtle"
                    }`}
                  >
                    {stage.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
