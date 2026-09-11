import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "cardnews.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS accounts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT UNIQUE NOT NULL,
            type        TEXT NOT NULL,
            genre       TEXT DEFAULT '헬스',
            followers   INTEGER DEFAULT 0,
            added_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS posts (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id          INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
            shortcode           TEXT UNIQUE NOT NULL,
            post_type           TEXT DEFAULT 'image',
            thumbnail_path      TEXT,
            caption             TEXT,
            translated_caption  TEXT,
            rewritten_caption   TEXT,
            likes               INTEGER DEFAULT 0,
            comments            INTEGER DEFAULT 0,
            views               INTEGER DEFAULT 0,
            engagement_rate     REAL DEFAULT 0,
            similarity_score    REAL,
            posted_at           DATETIME,
            collected_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_favorited        INTEGER DEFAULT 0
        );
    """)

    conn.commit()
    conn.close()


# ---------- Account CRUD ----------

def add_account(username: str, acc_type: str, genre: str = "헬스", followers: int = 0) -> int:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO accounts (username, type, genre, followers) VALUES (?, ?, ?, ?)",
            (username.lstrip("@"), acc_type, genre, followers)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def delete_account(account_id: int):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
        conn.commit()
    finally:
        conn.close()


def get_all_accounts():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM accounts ORDER BY added_at DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_account_followers(account_id: int, followers: int):
    conn = get_connection()
    try:
        conn.execute("UPDATE accounts SET followers = ? WHERE id = ?", (followers, account_id))
        conn.commit()
    finally:
        conn.close()


# ---------- Post CRUD ----------

def upsert_post(account_id: int, shortcode: str, data: dict):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO posts
                (account_id, shortcode, post_type, thumbnail_path, caption,
                 likes, comments, views, engagement_rate, posted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(shortcode) DO UPDATE SET
                likes           = excluded.likes,
                comments        = excluded.comments,
                views           = excluded.views,
                engagement_rate = excluded.engagement_rate,
                collected_at    = CURRENT_TIMESTAMP
        """, (
            account_id,
            shortcode,
            data.get("post_type", "image"),
            data.get("thumbnail_path", ""),
            data.get("caption", ""),
            data.get("likes", 0),
            data.get("comments", 0),
            data.get("views", 0),
            data.get("engagement_rate", 0.0),
            data.get("posted_at", ""),
        ))
        conn.commit()
    finally:
        conn.close()


def get_posts(acc_type_filter=None, min_er=0.0, sort_by="engagement_rate", limit=200):
    conn = get_connection()
    try:
        query = """
            SELECT p.*, a.username, a.type, a.genre, a.followers
            FROM posts p
            JOIN accounts a ON p.account_id = a.id
            WHERE p.engagement_rate >= ?
        """
        params = [min_er]
        if acc_type_filter and acc_type_filter != "전체":
            query += " AND a.type = ?"
            params.append(acc_type_filter)

        allowed_sort = {"engagement_rate", "likes", "comments", "collected_at"}
        col = sort_by if sort_by in allowed_sort else "engagement_rate"
        query += f" ORDER BY p.{col} DESC LIMIT ?"
        params.append(limit)

        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_post_by_id(post_id: int):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT p.*, a.username, a.type, a.followers FROM posts p JOIN accounts a ON p.account_id = a.id WHERE p.id = ?",
            (post_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_post_captions(post_id: int, translated: str = None, rewritten: str = None, similarity: float = None):
    conn = get_connection()
    try:
        fields = []
        params = []
        if translated is not None:
            fields.append("translated_caption = ?")
            params.append(translated)
        if rewritten is not None:
            fields.append("rewritten_caption = ?")
            params.append(rewritten)
        if similarity is not None:
            fields.append("similarity_score = ?")
            params.append(similarity)
        if not fields:
            return
        params.append(post_id)
        conn.execute(f"UPDATE posts SET {', '.join(fields)} WHERE id = ?", params)
        conn.commit()
    finally:
        conn.close()


def toggle_favorite(post_id: int):
    conn = get_connection()
    try:
        conn.execute("UPDATE posts SET is_favorited = 1 - is_favorited WHERE id = ?", (post_id,))
        conn.commit()
    finally:
        conn.close()
