from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db
import datetime

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
)

@router.get("/movies/{movie_id}/summary", response_model=schemas.MovieAnalytics)
def get_movie_summary(movie_id: int, start_date: datetime.date, end_date: datetime.date, db: Session = Depends(get_db)):
    return crud.get_movie_analytics(db, movie_id, start_date, end_date)
