from .auth import register_user
from .movie_service import add_movie, add_show, ensure_screen_seats


def seed_database(conn) -> None:
    movie_count = conn.execute("SELECT COUNT(*) AS c FROM movies").fetchone()["c"]
    user_count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
    if movie_count or user_count:
        return

    admin = register_user(conn, "Admin", "admin@example.com", "admin123")
    conn.execute("UPDATE users SET role='admin' WHERE id=?", (admin.id,))
    conn.commit()

    register_user(conn, "Demo User", "user@example.com", "user123")

    m1 = add_movie(conn, "The Last Ticket", "Drama", "125", "English", "8.2", "A small story about one last chance.")
    m2 = add_movie(conn, "Campus Nights", "Comedy", "110", "Hindi", "7.8", "Three friends try to survive one unforgettable week.")
    m3 = add_movie(conn, "Code Runner", "Thriller", "132", "English", "8.5", "A student discovers a program that should not exist.")

    for screen in ("Screen 1", "Screen 2"):
        ensure_screen_seats(conn, screen)

    add_show(conn, m1.id, "Screen 1", "2026-10-01", "18:30", "220")
    add_show(conn, m1.id, "Screen 1", "2026-10-02", "21:00", "250")
    add_show(conn, m2.id, "Screen 2", "2026-10-01", "17:00", "180")
    add_show(conn, m2.id, "Screen 2", "2026-10-03", "20:30", "200")
    add_show(conn, m3.id, "Screen 1", "2026-10-04", "19:00", "260")
