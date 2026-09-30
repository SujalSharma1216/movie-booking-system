import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.auth import login_user, register_user
from app.booking_service import BookingError, cancel_booking, create_booking, get_available_seats
from app.database import initialize_database, get_connection
from app.movie_service import add_movie, add_show, ensure_screen_seats
from app.reports import booking_summary


class MovieBookingSystemTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "test.db"
        initialize_database(db_path)
        self.conn = get_connection(db_path)
        self.user = register_user(self.conn, "Test User", "test@example.com", "secret1")
        movie = add_movie(self.conn, "Test Movie", "Drama", "120", "English", "8.0")
        ensure_screen_seats(self.conn, "Screen 1", rows=2, seats_per_row=4)
        self.show = add_show(self.conn, movie.id, "Screen 1", "2026-10-10", "18:00", "200")

    def tearDown(self):
        self.conn.close()
        self.temp_dir.cleanup()

    def test_registration_and_login(self):
        logged = login_user(self.conn, "test@example.com", "secret1")
        self.assertIsNotNone(logged)
        self.assertEqual(logged.id, self.user.id)

    def test_booking_reduces_available_seats(self):
        before = len(get_available_seats(self.conn, self.show.id))
        booking = create_booking(self.conn, self.user.id, self.show.id, ["A1", "A2"])
        after = len(get_available_seats(self.conn, self.show.id))
        self.assertEqual(before - 2, after)
        self.assertEqual(booking.total_amount, 400)

    def test_double_booking_is_rejected(self):
        create_booking(self.conn, self.user.id, self.show.id, ["A1"])
        with self.assertRaises(BookingError):
            create_booking(self.conn, self.user.id, self.show.id, ["A1"])

    def test_cancel_booking(self):
        booking = create_booking(self.conn, self.user.id, self.show.id, ["B1"])
        cancel_booking(self.conn, self.user.id, booking.id)
        summary = booking_summary(self.conn)
        self.assertEqual(summary["cancelled"], 1)

    def test_duplicate_email_is_rejected(self):
        with self.assertRaises(ValueError):
            register_user(self.conn, "Another", "test@example.com", "secret2")


if __name__ == "__main__":
    unittest.main()
