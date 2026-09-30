import sqlite3
from datetime import datetime
from .movie_service import get_show
from .models import Booking


class BookingError(Exception):
    pass


def get_all_seats(conn: sqlite3.Connection, screen: str):
    return conn.execute("SELECT id, seat_number FROM seats WHERE screen = ? ORDER BY seat_number", (screen,)).fetchall()


def get_booked_seat_ids(conn: sqlite3.Connection, show_id: int) -> set[int]:
    rows = conn.execute(
        """
        SELECT bs.seat_id
        FROM booking_seats bs
        JOIN bookings b ON b.id = bs.booking_id
        WHERE b.show_id = ? AND b.status = 'CONFIRMED'
        """,
        (show_id,),
    ).fetchall()
    return {row["seat_id"] for row in rows}


def get_available_seats(conn: sqlite3.Connection, show_id: int):
    show = get_show(conn, show_id)
    if not show:
        raise BookingError("Show not found.")
    seats = get_all_seats(conn, show.screen)
    booked = get_booked_seat_ids(conn, show_id)
    return [seat for seat in seats if seat["id"] not in booked]


def create_booking(conn: sqlite3.Connection, user_id: int, show_id: int, seat_numbers: list[str]) -> Booking:
    show = get_show(conn, show_id)
    if not show:
        raise BookingError("Show not found.")
    cleaned = [s.strip().upper() for s in seat_numbers if s.strip()]
    if not cleaned:
        raise BookingError("Select at least one seat.")
    if len(cleaned) != len(set(cleaned)):
        raise BookingError("Duplicate seats are not allowed.")

    seat_rows = conn.execute(
        f"SELECT id, seat_number FROM seats WHERE screen = ? AND seat_number IN ({','.join('?' for _ in cleaned)})",
        [show.screen] + cleaned,
    ).fetchall()
    if len(seat_rows) != len(cleaned):
        raise BookingError("One or more seat numbers are invalid for this screen.")

    seat_ids = [row["id"] for row in seat_rows]
    placeholders = ",".join("?" for _ in seat_ids)
    occupied = conn.execute(
        f"""
        SELECT bs.seat_id
        FROM booking_seats bs
        JOIN bookings b ON b.id = bs.booking_id
        WHERE b.show_id = ? AND b.status = 'CONFIRMED' AND bs.seat_id IN ({placeholders})
        """,
        [show_id] + seat_ids,
    ).fetchall()
    if occupied:
        raise BookingError("One or more selected seats are already booked.")

    total = round(show.price * len(seat_ids), 2)
    booked_at = datetime.now().isoformat(timespec="seconds")
    try:
        conn.execute("BEGIN")
        cursor = conn.execute(
            "INSERT INTO bookings(user_id, show_id, total_amount, booked_at, status) VALUES (?, ?, ?, ?, 'CONFIRMED')",
            (user_id, show_id, total, booked_at),
        )
        booking_id = cursor.lastrowid
        conn.executemany(
            "INSERT INTO booking_seats(booking_id, seat_id) VALUES (?, ?)",
            [(booking_id, seat_id) for seat_id in seat_ids],
        )
        conn.commit()
    except sqlite3.IntegrityError as exc:
        conn.rollback()
        raise BookingError("The booking could not be completed. Please try again.") from exc

    return get_booking(conn, booking_id)


def get_booking(conn: sqlite3.Connection, booking_id: int) -> Booking:
    row = conn.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    if not row:
        raise BookingError("Booking not found.")
    return Booking(**dict(row))


def get_booking_seats(conn: sqlite3.Connection, booking_id: int) -> list[str]:
    rows = conn.execute(
        """
        SELECT s.seat_number
        FROM booking_seats bs
        JOIN seats s ON s.id = bs.seat_id
        WHERE bs.booking_id = ?
        ORDER BY s.seat_number
        """,
        (booking_id,),
    ).fetchall()
    return [row["seat_number"] for row in rows]


def list_user_bookings(conn: sqlite3.Connection, user_id: int):
    return conn.execute(
        """
        SELECT b.id, m.title, s.show_date, s.show_time, s.screen,
               b.total_amount, b.booked_at, b.status,
               GROUP_CONCAT(bs2.seat_number, ', ') AS seats
        FROM bookings b
        JOIN shows s ON s.id = b.show_id
        JOIN movies m ON m.id = s.movie_id
        JOIN booking_seats bs ON bs.booking_id = b.id
        JOIN seats bs2 ON bs2.id = bs.seat_id
        WHERE b.user_id = ?
        GROUP BY b.id
        ORDER BY b.booked_at DESC
        """,
        (user_id,),
    ).fetchall()


def cancel_booking(conn: sqlite3.Connection, user_id: int, booking_id: int) -> None:
    row = conn.execute("SELECT user_id, status FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    if not row:
        raise BookingError("Booking not found.")
    if row["user_id"] != user_id:
        raise BookingError("You can only cancel your own bookings.")
    if row["status"] != "CONFIRMED":
        raise BookingError("Only confirmed bookings can be cancelled.")
    conn.execute("UPDATE bookings SET status = 'CANCELLED' WHERE id = ?", (booking_id,))
    conn.commit()
