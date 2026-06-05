import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "adxray.db")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            youtube_url TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            progress TEXT NOT NULL DEFAULT 'queued',
            stream_url TEXT,
            duration REAL,
            report_json TEXT,
            narrative_json TEXT DEFAULT '{}',
            defense_json TEXT DEFAULT '{}',
            video_name TEXT DEFAULT '',
            video_id_used TEXT DEFAULT '',
            error TEXT,
            created_at TEXT NOT NULL,
            completed_at TEXT
        );

        CREATE TABLE IF NOT EXISTS scenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
            start_time REAL NOT NULL,
            end_time REAL NOT NULL,
            description TEXT,
            overlay_text TEXT,
            duration REAL NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_scenes_job ON scenes(job_id);
    """)
    try:
        conn.execute("ALTER TABLE jobs ADD COLUMN defense_json TEXT DEFAULT '{}'")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()


init_db()
