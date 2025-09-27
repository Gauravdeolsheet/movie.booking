from sqlalchemy import (Column, Integer, String, DateTime, Float, ForeignKey, JSON, Text)
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    release_date = Column(DateTime, nullable=False)

class Theater(Base):
    __tablename__ = "theaters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    halls = relationship("Hall", back_populates="theater")

class Hall(Base):
    __tablename__ = "halls"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    theater_id = Column(Integer, ForeignKey("theaters.id"), nullable=False)
    # Example: {"A": 10, "B": 12, "C": 12}
    seating_layout = Column(JSON, nullable=False)
    
    theater = relationship("Theater", back_populates="halls")

class Show(Base):
    __tablename__ = "shows"
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    hall_id = Column(Integer, ForeignKey("halls.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    price_inr = Column(Float, nullable=False)

    movie = relationship("Movie")
    hall = relationship("Hall")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    show_id = Column(Integer, ForeignKey("shows.id"), nullable=False)
    user_id = Column(String, index=True) # Assuming a simple user identifier
    booking_time = Column(DateTime, default=datetime.datetime.utcnow)
    number_of_seats = Column(Integer, nullable=False)
    
    show = relationship("Show")
    booked_seats = relationship("BookedSeat", back_populates="booking")

class BookedSeat(Base):
    __tablename__ = "booked_seats"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    show_id = Column(Integer, ForeignKey("shows.id"), nullable=False)
    row_id = Column(String, nullable=False)
    seat_number = Column(Integer, nullable=False)
    
    booking = relationship("Booking", back_populates="booked_seats")
