from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, models
from ..database import get_db
from typing import List, Dict, Optional

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)

@router.post("/", response_model=schemas.Booking)
def create_booking(booking_info: schemas.BookingCreate, db: Session = Depends(get_db)):
    try:
        booking = crud.create_booking(db=db, booking_info=booking_info)
        # Reformat response to match schema
        booked_seats_schema = [schemas.Seat(row_id=s.row_id, seat_number=s.seat_number) for s in booking.booked_seats]
        return schemas.Booking(
            id=booking.id,
            show_id=booking.show_id,
            user_id=booking.user_id,
            booking_time=booking.booking_time,
            seats=booked_seats_schema
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An internal error occurred during booking.")

@router.get("/show/{show_id}/seats")
def get_seat_availability(show_id: int, db: Session = Depends(get_db)):
    show = db.query(models.Show).filter(models.Show.id == show_id).first()
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")

    hall = db.query(models.Hall).filter(models.Hall.id == show.hall_id).first()
    layout = hall.seating_layout
    
    booked_seats_db = crud.get_booked_seats(db, show_id)
    booked_seats_set = {(s.row_id, s.seat_number) for s in booked_seats_db}

    availability = {}
    for row_id, num_seats in layout.items():
        row_status = []
        for seat_num in range(1, num_seats + 1):
            status = "booked" if (row_id, seat_num) in booked_seats_set else "available"
            row_status.append({"seat_number": seat_num, "status": status})
        availability[row_id] = row_status
        
    return availability
