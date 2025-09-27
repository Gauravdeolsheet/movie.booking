from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from . import models, schemas
import datetime

# --- Movie CRUD ---
def create_movie(db: Session, movie: schemas.MovieCreate):
    db_movie = models.Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

def get_movie(db: Session, movie_id: int):
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()

# --- Theater & Hall CRUD ---
def create_theater(db: Session, theater: schemas.TheaterCreate):
    db_theater = models.Theater(**theater.dict())
    db.add(db_theater)
    db.commit()
    db.refresh(db_theater)
    return db_theater

def create_hall(db: Session, hall: schemas.HallCreate, theater_id: int):
    db_hall = models.Hall(**hall.dict(), theater_id=theater_id)
    db.add(db_hall)
    db.commit()
    db.refresh(db_hall)
    return db_hall

# --- Show CRUD ---
def create_show(db: Session, show: schemas.ShowCreate):
    db_show = models.Show(**show.dict())
    db.add(db_show)
    db.commit()
    db.refresh(db_show)
    return db_show

def get_shows_by_movie_and_date(db: Session, movie_id: int, date: datetime.date):
    start_of_day = datetime.datetime.combine(date, datetime.time.min)
    end_of_day = datetime.datetime.combine(date, datetime.time.max)
    return db.query(models.Show).filter(
        models.Show.movie_id == movie_id,
        models.Show.start_time >= start_of_day,
        models.Show.start_time <= end_of_day
    ).all()
    
# --- Booking Logic ---
def get_booked_seats(db: Session, show_id: int):
    return db.query(models.BookedSeat).filter(models.BookedSeat.show_id == show_id).all()

def create_booking(db: Session, booking_info: schemas.BookingCreate):
    # PESSIMISTIC LOCKING: Lock the show row to prevent concurrent modifications
    show = db.query(models.Show).filter(models.Show.id == booking_info.show_id).with_for_update().first()
    if not show:
        raise ValueError("Show not found")
        
    # Check if any requested seats are already booked
    for seat in booking_info.seats:
        is_booked = db.query(models.BookedSeat).filter(
            models.BookedSeat.show_id == booking_info.show_id,
            models.BookedSeat.row_id == seat.row_id,
            models.BookedSeat.seat_number == seat.seat_number
        ).first()
        if is_booked:
            raise ValueError(f"Seat {seat.row_id}{seat.seat_number} is already booked.")

    # Create the booking
    db_booking = models.Booking(
        show_id=booking_info.show_id,
        user_id=booking_info.user_id,
        number_of_seats=len(booking_info.seats)
    )
    db.add(db_booking)
    db.flush() # Use flush to get the booking ID before committing

    # Create the booked seat records
    for seat in booking_info.seats:
        db_booked_seat = models.BookedSeat(
            booking_id=db_booking.id,
            show_id=booking_info.show_id,
            row_id=seat.row_id,
            seat_number=seat.seat_number
        )
        db.add(db_booked_seat)
    
    db.commit()
    db.refresh(db_booking)
    return db_booking

# --- Analytics Logic ---
def get_movie_analytics(db: Session, movie_id: int, start_date: datetime.date, end_date: datetime.date):
    start_dt = datetime.datetime.combine(start_date, datetime.time.min)
    end_dt = datetime.datetime.combine(end_date, datetime.time.max)

    query = db.query(
        func.count(models.BookedSeat.id).label("total_tickets"),
        func.sum(models.Show.price_inr).label("gross_revenue")
    ).join(models.Booking, models.BookedSeat.booking_id == models.Booking.id)\
     .join(models.Show, models.Booking.show_id == models.Show.id)\
     .filter(
         models.Show.movie_id == movie_id,
         models.Booking.booking_time >= start_dt,
         models.Booking.booking_time <= end_dt
     ).first()

    return {
        "movie_id": movie_id,
        "total_tickets_sold": query.total_tickets if query.total_tickets else 0,
        "gross_revenue_inr": query.gross_revenue if query.gross_revenue else 0.0
    }
