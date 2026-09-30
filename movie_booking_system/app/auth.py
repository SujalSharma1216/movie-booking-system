import hashlib
import hmac
import os
import sqlite3
from typing import Optional
from .models import User
from .validators import validate_email, validate_password, require_text


def _hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
    return f"{salt.hex()}${digest.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split("$", 1)
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
    return hmac.compare_digest(candidate.hex(), digest_hex)


def register_user(conn: sqlite3.Connection, name: str, email: str, password: str) -> User:
    name = require_text(name, "Name")
    email = validate_email(email)
    password = validate_password(password)
    try:
        cursor = conn.execute(
            "INSERT INTO users(name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, _hash_password(password)),
        )
        conn.commit()
    except sqlite3.IntegrityError as exc:
        raise ValueError("An account with that email already exists.") from exc
    row = conn.execute("SELECT id, name, email, role FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return User(**dict(row))


def login_user(conn: sqlite3.Connection, email: str, password: str) -> Optional[User]:
    email = validate_email(email)
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if row and _verify_password(password, row["password_hash"]):
        return User(row["id"], row["name"], row["email"], row["role"])
    return None
