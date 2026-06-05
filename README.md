<div align="center">

# 🔬 Ad-Xray

**See Through the Persuasion Machine**

[![VideoDB](https://img.shields.io/badge/Powered_by-VideoDB-orange?style=for-the-badge)](https://videodb.io)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)

An AI-powered art project that exposes the hidden psychology of advertising — frame by frame.

</div>

---

Every advertisement is a carefully engineered psychological artifact. Behind a 20-second commercial are teams of marketers, psychologists, and behavioral scientists using decades of research to influence perception and behavior.

**Ad-Xray uses AI to deconstruct advertisements and expose the persuasive techniques embedded in every frame.** Instead of consuming an ad passively, viewers get a full psychological report revealing:

- A synthesized breakdown of the ad's manipulation strategy
- Emotional triggers and cognitive biases being exploited
- Key moments with on-screen overlay commentary
- Narrative analysis of spoken words and story arc

The result is an annotated video with overlaid commentary — plus a shareable report that makes the invisible visible.

---

## Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **VideoDB API Key** — get one free at [console.videodb.io](https://console.videodb.io)

### Setup

```bash
git clone https://github.com/video-db/ads-xray.git
cd ads-xray

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "VIDEO_DB_API_KEY=your_key_here" > .env

# Frontend
cd ../frontend
npm install
```

### Run

```bash
# Terminal 1 — Backend
cd backend && source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000), paste a YouTube ad URL, and click **X-Ray This Ad**.

---

## How It Works

```
YouTube URL → Upload → Shot Index → Intelligence Layer → Report + Annotated Video
                                  ↗ (audio transcript analysis)
```

### Dual-Stream Analysis

Ad-Xray processes ads through two independent streams:

**Visual Stream** — Shot-based scene indexing captures every distinct visual moment. Raw scene descriptions are fed into the intelligence layer for synthesis.

**Audio Stream** — Spoken words are transcribed and analyzed separately for narrative manipulation — persuasive language, story arcs, key phrases, and vocal tone.

### Intelligence Layer

An LLM synthesizes all raw data into a structured psychological report:

| Field | Description |
|-------|-------------|
| **Breakdown** | 2-paragraph critical analysis of the ad's overall strategy |
| **Primary Technique** | The single most powerful psychological move |
| **Emotional Triggers** | Tagged list — aspiration, fear, belonging, etc. |
| **Cognitive Biases** | Tagged list — halo effect, scarcity, authority, etc. |
| **Key Moments** | 3-10 timestamped insights with overlay text for the video |
| **Ad Archetype** | Aspirational Luxury, Fear-Based, Identity Sale, etc. |

### Video Assembly

Key moments are rendered as text overlays on the original video via VideoDB's programmable editor — crisp cyan pill badges at subtitle position.

### Report

Every analysis includes a full report: breakdown, technique classification, trigger/biases tags, narrative analysis (when audio is present), and key moments. One-click copy as Markdown for sharing.

---

## Architecture

```
ads-xray/
├── backend/                 # Python FastAPI
│   ├── main.py              # API routes
│   ├── pipeline.py          # Dual-stream analysis pipeline
│   ├── timeline_builder.py  # VideoDB Editor — overlay composition
│   ├── models.py            # Pydantic schemas
│   ├── db.py                # SQLite persistence
│   └── requirements.txt
├── frontend/                # Next.js 16
│   └── app/
│       ├── page.tsx         # Home — hero + URL input
│       ├── result/[jobId]/  # Full report + annotated video
│       └── components/      # URLInput, ProgressTracker, VideoPlayer
└── .gitignore
```

### API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analyze` | `POST` | Submit YouTube URL → returns `job_id` |
| `/api/status/{job_id}` | `GET` | Returns pipeline progress |
| `/api/result/{job_id}` | `GET` | Returns full report + stream URL + scenes |
| `/api/health` | `GET` | Health check |

### Design

- **Background:** Near-black (`#0A0A0A`) — X-ray film base
- **Primary accent:** Sky cyan (`#0EA5E9`) — clinical, scanning
- **Warning accent:** Amber (`#F59E0B`) — manipulation detected
- **Typography:** Geist (sans), JetBrains Mono (chrome/timestamps)
- **Cards:** Raised dark surfaces with hairline borders

---

## Philosophy

- **Transparency over persuasion** — The goal is not to tell viewers what to think, but to make the invisible visible
- **Viewer agency** — By understanding psychological triggers, viewers become conscious participants rather than passive targets
- **Art meets technology** — Ad-Xray is both a media artwork and a technological experiment, asking whether awareness itself is a form of resistance

---

## Community & Support

- **VideoDB Docs:** [docs.videodb.io](https://docs.videodb.io)
- **API Console:** [console.videodb.io](https://console.videodb.io)
- **Issues:** [GitHub Issues](https://github.com/video-db/ads-xray/issues)

---

<p align="center">An art project about power, perception, and manufactured desire.</p>
