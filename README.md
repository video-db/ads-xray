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

**Ad-Xray uses AI to deconstruct advertisements in real time and expose the persuasive techniques embedded in every frame.** Instead of consuming an ad passively, viewers see an annotated version that reveals:

- Emotional triggers being activated
- Cognitive biases being exploited
- Cultural symbols and aspirations being invoked
- The behavior the advertiser wants to trigger

The result is a video with overlaid commentary that makes the invisible visible.

---

## Demo

1. Paste a YouTube ad URL — a luxury car commercial, a perfume ad, an insurance spot
2. AI analyzes every scene for psychological manipulation
3. Watch the annotated video with timestamped overlays exposing each technique

*Example outputs coming soon.*

---

## Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **VideoDB API Key** — get one free at [console.videodb.io](https://console.videodb.io)

### Setup

```bash
# Clone
git clone https://github.com/video-db/Ad-Xray.git
cd Ad-Xray

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
YouTube URL → Upload → Scene Index (AI) → Commentary Extraction → Timeline Assembly → Annotated Stream
```

### 1. Upload
The YouTube ad is ingested into VideoDB via `coll.upload()`.

### 2. Scene Index
VideoDB's AI analyzes every scene using time-based extraction (5-second intervals, 2 frames per scene) with a forensic ad psychology prompt. Each scene returns structured output:

```
MANIPULATION: Halo Effect through Environmental Transfer
VISUAL: Stark cool white and gray tones, clinical overhead lighting...
EMOTION: Confidence, trust, sophistication...
EXPLOIT: Desire for superior quality, cutting-edge technology...
OVERLAY: This sterile, high-tech environment falsely elevates the product...
```

### 3. Commentary Extraction
The `OVERLAY` field is parsed from each scene's structured output — concise 10-15 word commentary ready for on-screen display.

### 4. Timeline Assembly
VideoDB's programmable editor composes a 2-track timeline:
- **Track 1:** Original video (1920x1080, `Fit.contain`)
- **Track 2:** Text overlays at each scene boundary — cyan background, white text, positioned at bottom

### 5. Delivery
The annotated video is delivered as an HLS stream URL — playable in any browser or embeddable anywhere.

---

## Architecture

```
Ad-Xray/
├── backend/                 # Python FastAPI
│   ├── main.py              # API routes (POST /analyze, GET /status, GET /result)
│   ├── pipeline.py          # 6-step analysis pipeline
│   ├── timeline_builder.py  # VideoDB Editor composition (VideoAsset + TextAsset)
│   ├── models.py            # Pydantic + SQLite models
│   ├── db.py                # SQLite job/scene persistence
│   └── requirements.txt
├── frontend/                # Next.js 16
│   └── app/
│       ├── page.tsx         # Home: hero + URL input + how-it-works
│       ├── result/[jobId]/  # Result: progress tracker + video player + scene breakdown
│       └── components/      # URLInput, ProgressTracker, VideoPlayer
└── .gitignore
```

### API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analyze` | `POST` | Submit YouTube URL → returns `job_id` |
| `/api/status/{job_id}` | `GET` | Returns status: pending → processing → completed/failed |
| `/api/result/{job_id}` | `GET` | Returns stream URL + scene breakdown with overlay text |
| `/api/health` | `GET` | Health check |

### Design

Ad-Xray uses a clinical "X-ray" aesthetic:
- **Background:** Near-black (`#0A0A0A`) — X-ray film base
- **Primary accent:** Sky cyan (`#0EA5E9`) — clinical, scanning
- **Warning accent:** Amber (`#F59E0B`) — manipulation detected
- **Typography:** Geist (sans), JetBrains Mono (chrome/timestamps)
- **Cards:** Raised dark surfaces with hairline borders

---

## Tested Ads

The pipeline has been validated across 4 distinct ad types:

| Ad | Duration | Type | Scenes | Status |
|----|----------|------|--------|--------|
| Audi A6 "Manipulation" | 45s | Product-focused, spoken words | 10 | ✅ |
| Chanel "Who Will Take It All?" | 136s | Silent luxury, fast cuts | 28 | ✅ |
| Patek Philippe "Generation" | 30s | Silent luxury, emotional | 6 | ✅ |
| Allstate "Mayhem Old Wiring" | 30s | Narrative, spoken words, humor | 6 | ✅ |

The pipeline handles silent ads, fast-cut luxury ads, dialogue-driven narratives, and short/long formats equally well.

---

## Philosophy

- **Transparency over persuasion** — The goal is not to tell viewers what to think, but to make the invisible visible
- **Viewer agency** — By understanding psychological triggers, viewers become conscious participants rather than passive targets
- **Art meets technology** — Ad-Xray is both a media artwork and a technological experiment, asking whether awareness itself is a form of resistance

---

## Community & Support

- **VideoDB Docs:** [docs.videodb.io](https://docs.videodb.io)
- **API Console:** [console.videodb.io](https://console.videodb.io)
- **Issues:** [GitHub Issues](https://github.com/video-db/Ad-Xray/issues)

---

<p align="center">An art project about power, perception, and manufactured desire.</p>
