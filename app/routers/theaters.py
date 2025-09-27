from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
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
    # Here you would check if theater_id exists
    return crud.create_hall(db=db, hall=hall, theater_id=theater_id)
