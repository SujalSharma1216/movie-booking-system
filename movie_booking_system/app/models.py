from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    name: str
    email: str
    role: str

@dataclass
class Movie:
    id: int
    title: str
    genre: str
    duration: int
    language: str
    rating: float
    description: str = ""

@dataclass
class Show:
    id: int
    movie_id: int
    screen: str
    show_date: str
    show_time: str
    price: float

@dataclass
class Booking:
    id: int
    user_id: int
    show_id: int
    total_amount: float
    booked_at: str
    status: str
