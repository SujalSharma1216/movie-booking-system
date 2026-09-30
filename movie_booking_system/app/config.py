from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "movie_booking.db"
LOG_PATH = BASE_DIR / "movie_booking.log"

DATA_DIR.mkdir(exist_ok=True)
