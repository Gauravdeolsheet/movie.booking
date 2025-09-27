from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, models
from ..database import get_db

router = APIRouter(
    prefix="/theaters",
    tags=["theaters"],
)

@router.post("/", response_model=schemas.Theater)
def create_theater(theater: schemas.TheaterCreate, db: Session = Depends(get_db)):
    return crud.create_theater(db=db, theater=theater)

@router.post("/{theater_id}/halls/", response_model=schemas.Hall)
def create_hall_for_theater(theater_id: int, hall: schemas.HallCreate, db: Session = Depends(get_db)):
    db_theater = db.query(models.Theater).filter(models.Theater.id == theater_id).first()
    if not db_theater:
        raise HTTPException(status_code=404, detail="Theater not found")

    # --- NEW VALIDATION LOGIC ---
    for row, seat_count in hall.seating_layout.items():
        if not isinstance(seat_count, int) or seat_count < 6:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid seat count for row '{row}'. Each row must have at least 6 seats."
            )
    # --- END OF VALIDATION ---

    return crud.create_hall(db=db, hall=hall, theater_id=theater_id)
