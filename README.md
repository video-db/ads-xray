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
- Manipulation intensity score (1-10) with color-coded severity
- Emotional triggers and cognitive biases being exploited
- Cultural symbols weaponized for persuasion
- Key moments with on-screen overlay commentary
- Narrative analysis of spoken words (or skipped when audio is insufficient)
- Defense strategies — actionable counter-tactics to resist each technique
- An empowerment message to reclaim cognitive autonomy

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

Open [http://localhost:3000](http://localhost:3000), enter your VideoDB API key, paste a YouTube ad URL, and click **X-Ray This Ad**.

> **Note:** Ad-Xray uses your personal VideoDB API key — no server-side secrets. Your key is stored locally in your browser and sent with each request. All video processing runs against your own VideoDB collection.

---

## How It Works

```
YouTube URL → Upload → Shot Index → Intelligence Layer → Audio Analysis → Defense Strategies → Annotated Video + Report
```

### Bring Your Own Key

Ad-Xray does not hold any API keys. Users authenticate with their own VideoDB key, stored in browser `localStorage`. Every API request includes `X-VideoDB-Key` — the key is validated before any job is queued. Each user's jobs are isolated by a SHA-256 hash of their key.

### Dual-Stream Analysis

Ad-Xray processes ads through independent streams running in parallel where possible:

**Visual Stream** — Shot-based scene indexing captures every distinct visual moment. Raw scene descriptions are fed into the intelligence layer. For long ads (>80K chars of scene data), analysis runs in parallel across multiple chunks and the results are merged.

**Audio Stream** — Spoken words are transcribed and analyzed separately. When the transcript is too sparse (silent ads, minimal dialogue), the LLM returns `insufficient_audio` and the narrative section is gracefully skipped — no hallucinated analysis from noise.

### Intelligence Layer

An LLM (VideoDB PRO model) synthesizes all raw data into a structured psychological report using an evidence→manipulation overlay pattern — every key moment explains *what* is visually shown and *how* it manipulates:

| Field | Description |
|-------|-------------|
| **Breakdown** | 2-paragraph critical analysis using - bullet points |
| **Manipulation Score** | 1-10 rating of overall manipulative intensity (never null) |
| **Primary Technique** | The single most powerful psychological move |
| **Emotional Triggers** | Tagged list — aspiration, fear, belonging, etc. |
| **Cognitive Biases** | Tagged list — halo effect, scarcity, authority, etc. |
| **Symbols** | Cultural symbols leveraged — `Sharp Suit=Power/Status` |
| **Key Moments** | 3-7 timestamped insights with overlay text (≥5s filter) |
| **Ad Archetype** | Aspirational Luxury, Fear-Based, Identity Sale, etc. |

### Defense Strategies

A dedicated LLM call takes the report summary and generates 3-5 actionable defense strategies — each targeting a specific manipulation technique with a practical counter-tactic and a defusing question to ask yourself. Every report ends with an empowerment message about media literacy and cognitive autonomy.

### Video Assembly

Key moments are rendered as text overlays on the original video via VideoDB's programmable editor — crisp cyan pill badges at subtitle position.

### Report & History

Every analysis includes: score badge, breakdown, technique + archetype, emotion/biases tags, symbols exploited, key moments timeline with start–end timestamps, narrative analysis (only when audio is meaningful), defense strategies, and empowerment message. One-click copy as Markdown or stream link for sharing.

The home page shows your 10 most recent analyses with technique labels and scores. The History page provides a paginated list of all past runs (10 per page).

---

## Architecture

```
ads-xray/
├── backend/                 # Python FastAPI
│   ├── main.py              # API routes + rate limiting + auth
│   ├── pipeline.py          # Dual-stream analysis pipeline
│   ├── timeline_builder.py  # VideoDB Editor — overlay composition
│   ├── models.py            # Pydantic schemas + validators
│   ├── db.py                # SQLite persistence
│   └── requirements.txt
├── frontend/                # Next.js 16 (App Router)
│   └── app/
│       ├── page.tsx         # Home — hero + URL input + recent runs
│       ├── history/         # Paginated analysis history
│       ├── result/[jobId]/  # Full report + annotated video
│       └── components/      # ApiKeyGate, URLInput, ProgressTracker,
│                            # VideoPlayer, HistoryCard
└── .gitignore
```

### API

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/validate-key` | `POST` | No | Validates a VideoDB API key |
| `/api/analyze` | `POST` | Key | Submit YouTube URL → returns `job_id` |
| `/api/status/{job_id}` | `GET` | Key | Returns pipeline progress |
| `/api/result/{job_id}` | `GET` | Key | Returns full report + stream URL + scenes |
| `/api/history` | `GET` | Key | Past runs with pagination (`?page=1&per_page=10`) |
| `/api/health` | `GET` | No | Health check with DB connectivity |

All `Key` endpoints require `X-VideoDB-Key` header and isolate data by key hash. Jobs are tied to the submitting key — no cross-user access.

### Security

| Protection | Implementation |
|------------|---------------|
| **Authentication** | User's VideoDB API key, validated per request |
| **Authorization** | All data scoped to API key SHA-256 hash |
| **Rate Limiting** | 5 POST/min per key on `/api/analyze` |
| **Concurrency** | Max 4 parallel analysis threads, 5th+ gets 503 |
| **Input Validation** | URL domain (`youtube.com`/`youtu.be`), scheme, length enforced |
| **SSRF Prevention** | URL hostname whitelist, no arbitrary URL fetching |
| **Body Size** | 64KB request limit (413 if exceeded) |
| **CORS** | Origin-restricted, GET/POST only, specific headers |
| **CSP** | Script/style/frame restrictions via `Content-Security-Policy` |
| **Headers** | `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff` |
| **Secrets** | No server-side API keys — BYO key model |
| **Error Sanitization** | All errors get user-friendly messages, tracebacks go to file logs only |

### Design

- **Background:** Near-black (`#0A0A0A`) — X-ray film base
- **Primary accent:** Sky cyan (`#0EA5E9`) — clinical, scanning
- **Warning accent:** Amber (`#F59E0B`) — manipulation detected
- **Danger accent:** Red (`#EF4444`) — high manipulation score
- **Success accent:** Green (`#22C55E`) — defense strategies
- **Typography:** Geist (sans), Geist Mono (timestamps/code)
- **Cards:** Raised dark surfaces with hairline borders

---

## Philosophy

- **Transparency over persuasion** — The goal is not to tell viewers what to think, but to make the invisible visible
- **Viewer agency** — By understanding psychological triggers, viewers become conscious participants rather than passive targets
- **Art meets technology** — Ad-Xray is both a media artwork and a technological experiment, asking whether awareness itself is a form of resistance
- **No gatekeepers** — You bring your own API key. The tool serves you, not the other way around

---

## Community & Support

- **VideoDB Docs:** [docs.videodb.io](https://docs.videodb.io)
- **API Console:** [console.videodb.io](https://console.videodb.io)
- **Issues:** [GitHub Issues](https://github.com/video-db/ads-xray/issues)

---

<p align="center">An art project about power, perception, and manufactured desire.</p>
