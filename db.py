# db.py
import sqlite3
from pathlib import Path
from typing import Iterable, Dict, Any, List

DB_PATH = Path("data") / "news.db"


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS headlines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            collected_at TEXT NOT NULL,
            title_hash TEXT NOT NULL,
            UNIQUE(source, title_hash)
        );
        """)
        conn.commit()


def upsert_headlines(items: Iterable[Dict[str, Any]]) -> int:
    """
    Inserts items; duplicates ignored due to UNIQUE(source, title_hash).
    Returns number of newly inserted rows.
    """
    inserted = 0
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        for it in items:
            try:
                cur.execute("""
                INSERT INTO headlines (source, title, url, collected_at, title_hash)
                VALUES (?, ?, ?, ?, ?)
                """, (it["source"], it["title"], it["url"], it["collected_at"], it["title_hash"]))
                inserted += 1
            except sqlite3.IntegrityError:
                # duplicate
                pass
        conn.commit()
    return inserted


def fetch_by_date(date_prefix: str) -> List[dict]:
    """
    date_prefix format: 'YYYY-MM-DD'
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT source, title, url, collected_at
            FROM headlines
            WHERE collected_at LIKE ?
            ORDER BY source, collected_at DESC
        """, (f"{date_prefix}%",)).fetchall()
    return [dict(r) for r in rows]
