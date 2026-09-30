import sqlite3
from datetime import datetime


def booking_summary(conn: sqlite3.Connection):
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS total_bookings,
            SUM(CASE WHEN status='CONFIRMED' THEN 1 ELSE 0 END) AS confirmed,
            SUM(CASE WHEN status='CANCELLED' THEN 1 ELSE 0 END) AS cancelled,
            COALESCE(SUM(CASE WHEN status='CONFIRMED' THEN total_amount ELSE 0 END), 0) AS revenue
        FROM bookings
        """
    ).fetchone()
    return dict(row)


def top_movies(conn: sqlite3.Connection):
    return conn.execute(
        """
        SELECT m.title, COUNT(b.id) AS bookings,
               COALESCE(SUM(CASE WHEN b.status='CONFIRMED' THEN b.total_amount ELSE 0 END), 0) AS revenue
        FROM movies m
        LEFT JOIN shows s ON s.movie_id = m.id
        LEFT JOIN bookings b ON b.show_id = s.id
        GROUP BY m.id
        ORDER BY bookings DESC, revenue DESC, m.title
        """
    ).fetchall()


def report_text(conn: sqlite3.Connection) -> str:
    summary = booking_summary(conn)
    lines = [
        "MOVIE BOOKING SYSTEM - ADMIN REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"Total bookings : {summary['total_bookings'] or 0}",
        f"Confirmed      : {summary['confirmed'] or 0}",
        f"Cancelled      : {summary['cancelled'] or 0}",
        f"Revenue        : Rs. {float(summary['revenue'] or 0):.2f}",
        "",
        "Movie-wise activity:",
    ]
    for row in top_movies(conn):
        lines.append(f"- {row['title']}: {row['bookings']} bookings, Rs. {float(row['revenue'] or 0):.2f} confirmed revenue")
    return "\n".join(lines)
