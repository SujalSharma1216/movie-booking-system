import logging
from .auth import login_user, register_user
from .booking_service import BookingError, cancel_booking, create_booking, get_available_seats, get_booking_seats, list_user_bookings
from .movie_service import add_movie, add_show, delete_movie, get_movie, list_movies, list_shows_for_movie, update_movie
from .reports import report_text
from .seed_data import seed_database
from .validators import validate_positive_int


logger = logging.getLogger(__name__)


def pause():
    input("\nPress Enter to continue...")


def show_movies(conn):
    search = input("Search movie/title/genre/language (leave blank for all): ")
    movies = list_movies(conn, search)
    if not movies:
        print("No movies found.")
        return
    print("\nID | Title | Genre | Duration | Language | Rating")
    print("-" * 75)
    for m in movies:
        print(f"{m.id} | {m.title} | {m.genre} | {m.duration} min | {m.language} | {m.rating}/10")


def register_flow(conn):
    try:
        user = register_user(conn, input("Name: "), input("Email: "), input("Password: "))
        print(f"Account created for {user.name}.")
    except ValueError as exc:
        print(f"Error: {exc}")


def login_flow(conn):
    try:
        user = login_user(conn, input("Email: "), input("Password: "))
        if not user:
            print("Invalid email or password.")
            return None
        print(f"Welcome, {user.name}!")
        return user
    except ValueError as exc:
        print(f"Error: {exc}")
        return None


def browse_and_book(conn, user):
    movies = list_movies(conn)
    if not movies:
        print("No movies available.")
        return
    print("\nMovies:")
    for m in movies:
        print(f"{m.id}. {m.title} ({m.genre}, {m.rating}/10)")
    try:
        movie_id = validate_positive_int(input("Movie ID: "), "Movie ID")
        if not get_movie(conn, movie_id):
            print("Movie not found.")
            return
        shows = list_shows_for_movie(conn, movie_id)
        if not shows:
            print("No shows available for this movie.")
            return
        print("\nShows:")
        for s in shows:
            print(f"{s.id}. {s.show_date} {s.show_time} | {s.screen} | Rs. {s.price:.2f}")
        show_id = validate_positive_int(input("Show ID: "), "Show ID")
        available = get_available_seats(conn, show_id)
        print("\nAvailable seats:")
        print(" ".join(seat["seat_number"] for seat in available))
        seat_input = input("Enter seats separated by comma (example A1,A2): ")
        booking = create_booking(conn, user.id, show_id, seat_input.split(","))
        print(f"\nBooking confirmed! Booking ID: {booking.id}")
        print(f"Seats: {', '.join(get_booking_seats(conn, booking.id))}")
        print(f"Total: Rs. {booking.total_amount:.2f}")
        logger.info("Booking %s created by user %s", booking.id, user.id)
    except (ValueError, BookingError) as exc:
        print(f"Error: {exc}")


def history_flow(conn, user):
    rows = list_user_bookings(conn, user.id)
    if not rows:
        print("No bookings found.")
        return
    print("\nBooking History")
    for row in rows:
        print(f"#{row['id']} | {row['title']} | {row['show_date']} {row['show_time']} | {row['seats']} | Rs. {row['total_amount']:.2f} | {row['status']}")


def cancel_flow(conn, user):
    try:
        booking_id = validate_positive_int(input("Booking ID to cancel: "), "Booking ID")
        cancel_booking(conn, user.id, booking_id)
        print("Booking cancelled.")
        logger.info("Booking %s cancelled by user %s", booking_id, user.id)
    except (ValueError, BookingError) as exc:
        print(f"Error: {exc}")


def admin_menu(conn, user):
    while True:
        print("\n--- ADMIN MENU ---")
        print("1. List movies")
        print("2. Add movie")
        print("3. Update movie")
        print("4. Add show")
        print("5. Delete movie")
        print("6. View report")
        print("7. Logout")
        choice = input("Choose: ").strip()
        if choice == "1":
            show_movies(conn); pause()
        elif choice == "2":
            try:
                movie = add_movie(conn, input("Title: "), input("Genre: "), input("Duration in minutes: "), input("Language: "), input("Rating (0-10): "), input("Description: "))
                print(f"Movie added with ID {movie.id}.")
            except ValueError as exc:
                print(f"Error: {exc}")
            pause()
        elif choice == "3":
            try:
                movie_id = validate_positive_int(input("Movie ID: "), "Movie ID")
                movie = get_movie(conn, movie_id)
                if not movie:
                    print("Movie not found.")
                else:
                    print("Leave a field blank to keep its current value.")
                    title = input(f"Title [{movie.title}]: ").strip()
                    genre = input(f"Genre [{movie.genre}]: ").strip()
                    duration = input(f"Duration [{movie.duration}]: ").strip()
                    language = input(f"Language [{movie.language}]: ").strip()
                    rating = input(f"Rating [{movie.rating}]: ").strip()
                    description = input(f"Description [{movie.description}]: ").strip()
                    fields = {
                        "title": title or movie.title,
                        "genre": genre or movie.genre,
                        "duration": duration or str(movie.duration),
                        "language": language or movie.language,
                        "rating": rating or str(movie.rating),
                        "description": description or movie.description,
                    }
                    update_movie(conn, movie_id, **fields)
                    print("Movie updated.")
            except ValueError as exc:
                print(f"Error: {exc}")
            pause()
        elif choice == "4":
            try:
                show = add_show(conn, validate_positive_int(input("Movie ID: "), "Movie ID"), input("Screen: "), input("Date YYYY-MM-DD: "), input("Time HH:MM: "), input("Price: "))
                from .movie_service import ensure_screen_seats
                ensure_screen_seats(conn, show.screen)
                print(f"Show added with ID {show.id}.")
            except ValueError as exc:
                print(f"Error: {exc}")
            pause()
        elif choice == "5":
            try:
                delete_movie(conn, validate_positive_int(input("Movie ID: "), "Movie ID"))
                print("Movie deleted.")
            except ValueError as exc:
                print(f"Error: {exc}")
            pause()
        elif choice == "6":
            print("\n" + report_text(conn)); pause()
        elif choice == "7":
            return
        else:
            print("Please choose a valid option.")


def user_menu(conn, user):
    while True:
        print("\n--- USER MENU ---")
        print("1. Browse movies")
        print("2. Book tickets")
        print("3. Booking history")
        print("4. Cancel booking")
        print("5. Logout")
        choice = input("Choose: ").strip()
        if choice == "1":
            show_movies(conn); pause()
        elif choice == "2":
            browse_and_book(conn, user); pause()
        elif choice == "3":
            history_flow(conn, user); pause()
        elif choice == "4":
            cancel_flow(conn, user); pause()
        elif choice == "5":
            return
        else:
            print("Please choose a valid option.")


def run(conn):
    seed_database(conn)
    logger.info("Application started")
    while True:
        print("\n==============================")
        print("     MOVIE BOOKING SYSTEM")
        print("==============================")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose: ").strip()
        if choice == "1":
            register_flow(conn); pause()
        elif choice == "2":
            user = login_flow(conn)
            if user:
                if user.role == "admin":
                    admin_menu(conn, user)
                else:
                    user_menu(conn, user)
        elif choice == "3":
            print("Thank you for using the Movie Booking System!")
            return
        else:
            print("Please choose a valid option.")
