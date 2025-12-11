import sqlite3
import hashlib
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "wrapped.db"


def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_hash TEXT UNIQUE NOT NULL,
            total_words INTEGER,
            total_conversations INTEGER,
            total_messages INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    conn.commit()
    conn.close()


def get_file_hash(data):
    """Generate a hash from the conversations data to uniquely identify a user."""
    if not data:
        return None

    unique_str = f"{len(data)}:{data[0].get('id', '')}:{data[-1].get('id', '')}"
    return hashlib.sha256(unique_str.encode()).hexdigest()


def save_user_stats(file_hash, total_words, total_conversations, total_messages):
    """Save or update user stats in the database (anonymized)."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE stats 
            SET total_words = ?, total_conversations = ?, total_messages = ?, updated_at = CURRENT_TIMESTAMP
            WHERE file_hash = ?
        """,
            (total_words, total_conversations, total_messages, file_hash),
        )

        if cursor.rowcount == 0:
            cursor.execute(
                """
                INSERT INTO stats (file_hash, total_words, total_conversations, total_messages)
                VALUES (?, ?, ?, ?)
            """,
                (file_hash, total_words, total_conversations, total_messages),
            )

        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving user stats: {e}")
        return False
    finally:
        conn.close()


def get_percentile(file_hash, metric="total_words"):
    """Get user's percentile ranking for a metric (0-100)."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    valid_metrics = ["total_words", "total_conversations", "total_messages"]
    if metric not in valid_metrics:
        metric = "total_words"

    try:
        cursor.execute(
            f"""
            SELECT {metric} FROM stats WHERE file_hash = ?
        """,
            (file_hash,),
        )

        result = cursor.fetchone()
        if not result:
            return None

        user_value = result[0]

        cursor.execute(
            f"""
            SELECT COUNT(*) FROM stats WHERE {metric} <= ?
        """,
            (user_value,),
        )

        count_below = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM stats")
        total = cursor.fetchone()[0]

        percentile = (count_below / total) * 100 if total > 0 else 0
        return percentile
    finally:
        conn.close()


def get_stats_summary():
    """Get aggregate stats (averages, medians) for comparison."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT 
                AVG(total_words) as avg_words,
                AVG(total_conversations) as avg_convos,
                AVG(total_messages) as avg_messages,
                COUNT(*) as total_users
            FROM stats
        """
        )

        result = cursor.fetchone()
        return {
            "avg_words": result[0],
            "avg_conversations": result[1],
            "avg_messages": result[2],
            "total_users": result[3],
        }
    finally:
        conn.close()
