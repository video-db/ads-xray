"use client";

import type { HistoryRun } from "@/app/page";

function formatTimeAgo(iso: string): string {
  const now = Date.now();
  const then = new Date(iso).getTime();
  const mins = Math.floor((now - then) / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export default function HistoryCard({
  run,
  onClick,
}: {
  run: HistoryRun;
  onClick: () => void;
}) {
  const score = run.manipulation_score || 0;

  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-3 px-4 py-3 rounded-card bg-surface border border-border hover:border-primary/30 transition-all duration-150 cursor-pointer text-left group"
    >
      <span
        className={`w-2 h-2 rounded-full flex-shrink-0 ${
          run.status === "failed" ? "bg-danger" : "bg-success"
        }`}
      />
      <div className="flex-1 min-w-0">
        <span className="text-sm text-foreground block truncate">
          {run.video_name || "Untitled"}
        </span>
        <span className="text-[11px] text-text-subtle block truncate">
          {run.primary_technique && `${run.primary_technique} · `}
          {run.duration ? `${Math.round(run.duration)}s` : ""}
          {run.duration ? " · " : ""}
          {formatTimeAgo(run.created_at)}
        </span>
      </div>
      {score > 0 && (
        <span
          className={`text-xs font-mono flex-shrink-0 ${
            score >= 8 ? "text-danger" : score >= 6 ? "text-warning" : "text-success"
          }`}
        >
          {score}/10
        </span>
      )}
    </button>
  );
}
