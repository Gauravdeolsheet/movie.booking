from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db
from typing import List
import datetime

router = APIRouter(
    prefix="/shows",
    tags=["shows"],
)

@router.post("/", response_model=schemas.Show)
def create_show(show: schemas.ShowCreate, db: Session = Depends(get_db)):
    return crud.create_show(db=db, show=show)

@router.get("/by-movie/{movie_id}", response_model=List[schemas.Show])
def get_shows(movie_id: int, date: datetime.date, db: Session = Depends(get_db)):
    return crud.get_shows_by_movie_and_date(db=db, movie_id=movie_id, date=date)
