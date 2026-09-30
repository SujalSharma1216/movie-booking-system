import sqlite3
from typing import Optional
from .models import Movie, Show
from .validators import require_text, validate_positive_int, validate_rating, validate_price, validate_date, validate_time


def list_movies(conn: sqlite3.Connection, search: str = "") -> list[Movie]:
    if search.strip():
        like = f"%{search.strip()}%"
        rows = conn.execute(
            "SELECT * FROM movies WHERE title LIKE ? OR genre LIKE ? OR language LIKE ? ORDER BY title",
            (like, like, like),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM movies ORDER BY title").fetchall()
    return [Movie(**dict(row)) for row in rows]


def get_movie(conn: sqlite3.Connection, movie_id: int) -> Optional[Movie]:
    row = conn.execute("SELECT * FROM movies WHERE id = ?", (movie_id,)).fetchone()
    return Movie(**dict(row)) if row else None


def add_movie(conn: sqlite3.Connection, title: str, genre: str, duration: str, language: str, rating: str, description: str = "") -> Movie:
    title = require_text(title, "Title")
    genre = require_text(genre, "Genre")
    language = require_text(language, "Language")
    duration_i = validate_positive_int(duration, "Duration")
    rating_f = validate_rating(rating)
    cursor = conn.execute(
        "INSERT INTO movies(title, genre, duration, language, rating, description) VALUES (?, ?, ?, ?, ?, ?)",
        (title, genre, duration_i, language, rating_f, description.strip()),
    )
    conn.commit()
    return get_movie(conn, cursor.lastrowid)


def update_movie(conn: sqlite3.Connection, movie_id: int, **fields) -> Movie:
    allowed = {"title", "genre", "duration", "language", "rating", "description"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        raise ValueError("No movie fields were supplied.")
    if "title" in updates:
        updates["title"] = require_text(str(updates["title"]), "Title")
    if "genre" in updates:
        updates["genre"] = require_text(str(updates["genre"]), "Genre")
    if "language" in updates:
        updates["language"] = require_text(str(updates["language"]), "Language")
    if "duration" in updates:
        updates["duration"] = validate_positive_int(str(updates["duration"]), "Duration")
    if "rating" in updates:
        updates["rating"] = validate_rating(str(updates["rating"]))
    if "description" in updates:
        updates["description"] = str(updates["description"]).strip()
    set_clause = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [movie_id]
    cur = conn.execute(f"UPDATE movies SET {set_clause} WHERE id = ?", values)
    if cur.rowcount == 0:
        raise ValueError("Movie not found.")
    conn.commit()
    return get_movie(conn, movie_id)


def delete_movie(conn: sqlite3.Connection, movie_id: int) -> None:
    cur = conn.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    if cur.rowcount == 0:
        raise ValueError("Movie not found.")
    conn.commit()


def add_show(conn: sqlite3.Connection, movie_id: int, screen: str, show_date: str, show_time: str, price: str) -> Show:
    if not get_movie(conn, movie_id):
        raise ValueError("Movie not found.")
    screen = require_text(screen, "Screen")
    show_date = validate_date(show_date)
    show_time = validate_time(show_time)
    price_f = validate_price(price)
    cursor = conn.execute(
        "INSERT INTO shows(movie_id, screen, show_date, show_time, price) VALUES (?, ?, ?, ?, ?)",
        (movie_id, screen, show_date, show_time, price_f),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM shows WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return Show(**dict(row))


def list_shows_for_movie(conn: sqlite3.Connection, movie_id: int) -> list[Show]:
    rows = conn.execute("SELECT * FROM shows WHERE movie_id = ? ORDER BY show_date, show_time", (movie_id,)).fetchall()
    return [Show(**dict(row)) for row in rows]


def get_show(conn: sqlite3.Connection, show_id: int) -> Optional[Show]:
    row = conn.execute("SELECT * FROM shows WHERE id = ?", (show_id,)).fetchone()
    return Show(**dict(row)) if row else None


def ensure_screen_seats(conn: sqlite3.Connection, screen: str, rows: int = 5, seats_per_row: int = 8) -> None:
    for r in range(rows):
        letter = chr(ord('A') + r)
        for n in range(1, seats_per_row + 1):
            conn.execute(
                "INSERT OR IGNORE INTO seats(screen, seat_number) VALUES (?, ?)",
                (screen, f"{letter}{n}"),
            )
    conn.commit()
