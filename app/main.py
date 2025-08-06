from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional

from . import crud, models, schemas, auth
from .database import SessionLocal, engine, get_db
from .config import settings
from .services.pokeapi import pokeapi_service

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pokemon Rater", description="Rate and analyze Pokemon")

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize admin user
def init_admin_user():
    db = SessionLocal()
    try:
        existing_user = crud.get_user(db, settings.admin_username)
        if not existing_user:
            hashed_password = auth.get_password_hash(settings.admin_password)
            admin_user = models.User(
                username=settings.admin_username,
                hashed_password=hashed_password,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print(f"Created admin user: {settings.admin_username}")
    finally:
        db.close()

# Initialize admin user on startup
@app.on_event("startup")
async def startup_event():
    init_admin_user()

# Authentication endpoints
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Pokemon endpoints
@app.get("/api/pokemon", response_model=List[schemas.Pokemon])
def get_pokemon_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pokemon = crud.get_pokemon_list(db, skip=skip, limit=limit)
    return pokemon

@app.get("/api/pokemon/{pokemon_name}", response_model=schemas.PokemonWithRating)
def get_pokemon_with_rating(pokemon_name: str, db: Session = Depends(get_db)):
    result = crud.get_pokemon_with_rating(db, pokemon_name)
    return result

@app.get("/api/pokemon/search/{query}")
def search_pokemon(query: str, db: Session = Depends(get_db)):
    pokemon = crud.search_pokemon(db, query)
    return pokemon

@app.get("/api/unrated-pokemon")
def get_unrated_pokemon(limit: int = 10, db: Session = Depends(get_db)):
    pokemon = crud.get_unrated_pokemon(db, limit)
    return pokemon

# Rating endpoints
@app.post("/api/rate", response_model=schemas.Rating)
def rate_pokemon(
    rating: schemas.RatingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    return crud.create_or_update_rating(db, rating)

# Analytics endpoints
@app.get("/api/analytics/top-rated")
def get_top_rated(limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_top_rated_pokemon(db, limit)

@app.get("/api/analytics/bottom-rated")
def get_bottom_rated(limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_bottom_rated_pokemon(db, limit)

@app.get("/api/analytics/statistics")
def get_statistics(db: Session = Depends(get_db)):
    return crud.get_rating_statistics(db)

@app.get("/api/analytics/by-type/{pokemon_type}")
def get_ratings_by_type(pokemon_type: str, db: Session = Depends(get_db)):
    return crud.get_ratings_by_type(db, pokemon_type)

@app.get("/api/analytics/by-generation/{generation}")
def get_ratings_by_generation(generation: int, db: Session = Depends(get_db)):
    return crud.get_ratings_by_generation(db, generation)

# Web interface endpoints
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/rate")
async def rate_page(request: Request):
    return templates.TemplateResponse("rate.html", {"request": request})

@app.get("/analytics")
async def analytics_page(request: Request):
    return templates.TemplateResponse("analytics.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)