import os
import sqlite3
from typing import List, Tuple
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("MEMORY_DB_PATH", "storage/memory/chat.db")

def init_memory():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_msg TEXT NOT NULL,
            bot_msg TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_turn(user_msg: str, bot_msg: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO chat_history (user_msg, bot_msg) VALUES (?, ?)", (user_msg, bot_msg))
    conn.commit()
    conn.close()

def get_last_turns(limit: int = 8) -> List[Tuple[str, str]]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_msg, bot_msg FROM chat_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    rows.reverse()
    return rows

