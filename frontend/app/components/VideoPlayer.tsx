interface SceneResult {
  start_time: number;
  end_time: number;
  overlay_text: string;
  description: string;
}

interface VideoPlayerProps {
  streamUrl: string;
  scenes?: SceneResult[];
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export default function VideoPlayer({ streamUrl, scenes }: VideoPlayerProps) {
  return (
    <div className="w-full max-w-5xl mx-auto">
      <div className="aspect-video rounded-card overflow-hidden bg-surface border border-border shadow-2xl">
        <video
          src={streamUrl}
          controls
          className="w-full h-full object-contain"
          poster="/api/placeholder"
        />
      </div>

      {scenes && scenes.length > 0 && (
        <div className="mt-8 space-y-3">
          <h3 className="text-lg font-light text-foreground flex items-center gap-2">
            <span className="text-primary">Scene Breakdown</span>
            <span className="text-text-subtle text-sm font-mono">
              {scenes.length} scenes detected
            </span>
          </h3>
          <div className="space-y-2">
            {scenes.map((scene, i) => (
              <div
                key={i}
                className="group flex items-start gap-4 p-4 rounded-card bg-surface border border-border
                  hover:border-primary/30 transition-all duration-200"
              >
                <div className="flex-shrink-0 w-20 text-center">
                  <div className="text-xs font-mono text-text-subtle uppercase tracking-wider">
                    Scene {i + 1}
                  </div>
                  <div className="text-sm font-mono text-primary mt-1">
                    {formatTime(scene.start_time)}
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-base text-foreground leading-relaxed">
                    {scene.overlay_text}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
