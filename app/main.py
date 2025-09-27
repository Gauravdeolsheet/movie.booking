from fastapi import FastAPI
from .database import engine
from . import models
from .routers import movies, theaters, shows, bookings, analytics

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Movie Ticket Booking API",
    description="API for a movie ticket booking system.",
    version="1.0.0"
)

app.include_router(movies.router)
app.include_router(theaters.router)
app.include_router(shows.router)
app.include_router(bookings.router)
app.include_router(analytics.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Movie Ticket Booking API!"}

