import sqlite3
import os
import re

DB_FOLDER = "movie_databases"


def get_database_name(movie_name):
    clean = re.sub(r"[^\w\s-]", "", movie_name).strip().replace(" ", "_").lower()

    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)

    return os.path.join(DB_FOLDER, f"{clean}.db")


def create_database_if_not_exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_name TEXT NOT NULL,
            tomatometer_score TEXT,
            audience_score TEXT,
            storyline TEXT,
            rating TEXT,
            genres TEXT,
            review_1 TEXT,
            review_2 TEXT,
            review_3 TEXT,
            review_4 TEXT,
            review_5 TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def insert_movie_data(db_path, movie_data):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO movies (
            movie_name, tomatometer_score, audience_score,
            storyline, rating, genres,
            review_1, review_2, review_3, review_4, review_5,
            status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        movie_data.get("movie_name", ""),
        movie_data.get("tomatometer_score", ""),
        movie_data.get("audience_score", ""),
        movie_data.get("storyline", ""),
        movie_data.get("rating", ""),
        movie_data.get("genres", ""),
        movie_data.get("review_1", ""),
        movie_data.get("review_2", ""),
        movie_data.get("review_3", ""),
        movie_data.get("review_4", ""),
        movie_data.get("review_5", ""),
        movie_data.get("status", "")
    ))

    conn.commit()
    conn.close()
