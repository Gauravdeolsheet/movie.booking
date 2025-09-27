from pydantic import BaseModel
from typing import List, Dict, Optional
import datetime

# --- Movie Schemas ---
class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration_minutes: int
    release_date: datetime.date

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int
    class Config:
        from_attributes = True

# --- Theater Schemas ---
class TheaterBase(BaseModel):
    name: str
    address: str
    city: str

class TheaterCreate(TheaterBase):
    pass

class Theater(TheaterBase):
    id: int
    class Config:
        from_attributes = True

# --- Hall Schemas ---
class HallBase(BaseModel):
    name: str
    seating_layout: Dict[str, int] # e.g. {"A": 10, "B": 12}

class HallCreate(HallBase):
    pass

class Hall(HallBase):
    id: int
    theater_id: int
    class Config:
        from_attributes = True

# --- Show Schemas ---
class ShowBase(BaseModel):
    movie_id: int
    hall_id: int
    start_time: datetime.datetime
    end_time: datetime.datetime
    price_inr: float

class ShowCreate(ShowBase):
    pass

class Show(ShowBase):
    id: int
    class Config:
        from_attributes = True

# --- Booking Schemas ---
class Seat(BaseModel):
    row_id: str
    seat_number: int

class BookingCreate(BaseModel):
    show_id: int
    user_id: str
    seats: List[Seat]

class Booking(BaseModel):
    id: int
    show_id: int
    user_id: str
    booking_time: datetime.datetime
    seats: List[Seat]

    class Config:
        from_attributes = True

# --- Analytics Schemas ---
class MovieAnalytics(BaseModel):
    movie_id: int
    total_tickets_sold: int
    gross_revenue_inr: float
