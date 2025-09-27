from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/movies",
    tags=["movies"],
)

@router.post("/", response_model=schemas.Movie)
def create_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    return crud.create_movie(db=db, movie=movie)

@router.get("/{movie_id}", response_model=schemas.Movie)
def read_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = crud.get_movie(db, movie_id=movie_id)
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return db_movie
