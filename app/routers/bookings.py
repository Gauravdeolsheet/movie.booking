from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, models
from ..database import get_db
from typing import List, Dict, Optional, Union

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)

@router.post(
    "/request",
    response_model=Union[schemas.BookingConfirmation, schemas.BookingSuggestionResponse],
    summary="Request and book seats, with suggestions on failure"
)
def request_seats(request: schemas.SeatRequest, db: Session = Depends(get_db)):
    """
    Attempts to find and book a contiguous block of seats for a show.
    - If successful, it books the first available block and returns a confirmation.
    - If no contiguous block is available, it suggests other showtimes.
    """
    available_seats_map = crud.get_available_seats_for_show(db, request.show_id)
    contiguous_blocks = crud.find_contiguous_seats(available_seats_map, request.number_of_seats)

    if not contiguous_blocks:
        alternatives = crud.find_alternative_shows(db, request.show_id, request.number_of_seats)
        if not alternatives:
            raise HTTPException(status_code=404, detail="No contiguous seats available for this show, and no alternative showtimes found.")
        
        return schemas.BookingSuggestionResponse(
            message="Could not find contiguous seats for the requested show. Here are some alternatives:",
            suggestions=alternatives
        )

    seats_to_book = contiguous_blocks[0]
    
    try:
        booking_info = schemas.BookingCreate(
            show_id=request.show_id,
            user_id=request.user_id,
            seats=seats_to_book
        )
        booking = crud.create_booking(db=db, booking_info=booking_info)
        
        booked_seats_schema = [schemas.Seat(row_id=s.row_id, seat_number=s.seat_number) for s in booking.booked_seats]
        booking_response = schemas.Booking(
            id=booking.id,
            show_id=booking.show_id,
            user_id=booking.user_id,
            booking_time=booking.booking_time,
            seats=booked_seats_schema
        )
        return schemas.BookingConfirmation(
            booking=booking_response,
            message=f"Successfully booked {request.number_of_seats} seats."
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=f"Booking failed due to a conflict: {e}")

# (Keep original endpoints for direct booking and seat checking)
@router.post("/", response_model=schemas.Booking)
def create_booking(booking_info: schemas.BookingCreate, db: Session = Depends(get_db)):
    try:
        booking = crud.create_booking(db=db, booking_info=booking_info)
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
