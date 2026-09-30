import logging
import sys
from .config import LOG_PATH
from .database import get_connection, initialize_database
from .cli import run


def configure_logging() -> None:
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def main() -> None:
    configure_logging()
    initialize_database()
    with get_connection() as conn:
        run(conn)


if __name__ == "__main__":
    main()
