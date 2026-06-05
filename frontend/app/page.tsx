"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import URLInput from "./components/URLInput";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (url: string) => {
    setSubmitting(true);
    setError("");

    try {
      const res = await fetch(`${API_URL}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ youtube_url: url }),
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
      <section className="flex-1 flex flex-col items-center justify-center px-6 py-24 min-h-[80vh]">
        <div className="text-center max-w-3xl mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface border border-border mb-8">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            <span className="text-xs font-mono text-text-muted uppercase tracking-widest">
              AI-Powered Ad Deconstruction
            </span>
          </div>

          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-light tracking-tight text-foreground leading-[1.1]">
            See Through the
            <br />
            <span className="text-primary">Persuasion Machine</span>
          </h1>

          <p className="mt-6 text-lg text-text-muted max-w-xl mx-auto leading-relaxed">
            Every ad is engineered by teams of psychologists to manipulate what you
            think, feel, and buy. Ad-Xray uses AI to expose the hidden techniques
            behind every frame — in real time.
          </p>
        </div>

        <URLInput onSubmit={handleSubmit} disabled={submitting} />

        {error && (
          <p className="mt-4 text-sm text-danger">{error}</p>
        )}
      </section>

      <section className="border-t border-border py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <span className="text-xs font-mono text-primary uppercase tracking-widest">
              How It Works
            </span>
            <h2 className="text-3xl sm:text-4xl font-light text-foreground mt-4">
              From passive viewer to critical observer
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                step: "01",
                title: "Paste any YouTube ad",
                desc: "Drop in a link to a car commercial, perfume ad, insurance spot — anything designed to sell.",
                icon: (
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                ),
              },
              {
                step: "02",
                title: "AI deconstructs it",
                desc: "Our AI analyzes every scene — identifying emotional triggers, cognitive biases, and persuasive techniques frame by frame.",
                icon: (
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
                  </svg>
                ),
              },
              {
                step: "03",
                title: "Watch the annotated result",
                desc: "See the original ad play with real-time overlays exposing every manipulation — making the invisible visible.",
                icon: (
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                ),
              },
            ].map((item) => (
              <div
                key={item.step}
                className="group p-8 rounded-card bg-surface border border-border
                  hover:border-primary/30 transition-all duration-200"
              >
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary mb-5 group-hover:bg-primary/20 transition-colors">
                  {item.icon}
                </div>
                <div className="text-xs font-mono text-primary mb-2">{item.step}</div>
                <h3 className="text-lg font-medium text-foreground mb-2">{item.title}</h3>
                <p className="text-sm text-text-muted leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="border-t border-border py-24 px-6 bg-surface">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-light text-foreground mb-6">
            Why This Exists
          </h2>
          <p className="text-text-muted leading-relaxed text-lg max-w-2xl mx-auto">
            Brands spend billions on teams of psychologists, behavioral scientists,
            and filmmakers to engineer desire. The viewer has none of these tools.
            Ad-Xray is an{" "}
            <span className="text-primary">artistic and technological intervention</span>{" "}
            designed to restore balance — making the invisible mechanics of persuasion
            visible to everyone.
          </p>
        </div>
      </section>

      <footer className="border-t border-border py-12 px-6">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm font-mono text-primary uppercase tracking-widest">Ad-Xray</span>
          </div>
          <p className="text-xs text-text-subtle">
            An art project about power, perception, and manufactured desire.
          </p>
        </div>
      </footer>
    </main>
  );
}
