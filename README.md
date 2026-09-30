# Movie Booking System

A simple Movie Booking System built with **Python** and **SQLite**. The project focuses on clean modular programming, CRUD operations, input validation, database transactions, basic authentication, booking management, reporting, and testing.

## Features

- User registration and login
- Password hashing using PBKDF2-HMAC-SHA256
- Admin and normal-user roles
- Browse and search movies
- Admin CRUD for movies (create, read, update, delete)
- Add movie shows with date, time, screen and price
- Automatic seat creation for screens
- View available seats
- Book multiple seats in one transaction
- Prevent double-booking
- View booking history
- Cancel bookings
- Admin booking/revenue report
- File logging
- Validation and friendly error messages
- Unit tests using Python `unittest`

## Technologies / Tools

- Python 3.10+
- SQLite3
- Python standard library
- Git / GitHub
- Mermaid diagrams (documentation)

## Project Structure

```text
movie_booking_system/
|-- app.py
|-- requirements.txt
|-- README.md
|-- statement.md
|-- .gitignore
|-- app/
|   |-- __init__.py
|   |-- auth.py
|   |-- booking_service.py
|   |-- cli.py
|   |-- config.py
|   |-- database.py
|   |-- main.py
|   |-- models.py
|   |-- movie_service.py
|   |-- reports.py
|   |-- seed_data.py
|   `-- validators.py
|-- data/
|-- docs/
|   `-- diagrams.md
`-- tests/
    `-- test_system.py
```

## How to Run

1. Install Python 3.10 or newer.
2. Open a terminal in the project folder.
3. Run:

```bash
python app.py
```

The first run automatically creates the SQLite database and inserts sample data.

### Demo accounts

- Admin: `admin@example.com` / `admin123`
- User: `user@example.com` / `user123`

## Testing

Run:

```bash
python -m unittest discover -s tests -v
```

No external testing library is required.

## Git / GitHub

Suggested commands:

```bash
git init
git add .
git commit -m "Initial Movie Booking System project"
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```

## Design Notes

The application uses a small layered structure:

- `cli.py` handles user interaction.
- `auth.py` handles registration/login.
- `movie_service.py` handles movie and show operations.
- `booking_service.py` handles seat availability and bookings.
- `reports.py` generates admin analytics.
- `database.py` creates and connects to SQLite.
- `validators.py` keeps input rules separate from business logic.

This is intentionally kept understandable for a first-year student rather than using a large framework.
