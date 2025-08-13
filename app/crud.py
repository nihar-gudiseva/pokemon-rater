from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from typing import List, Optional, Dict, Any
from . import models, schemas


def get_pokemon_by_name(db: Session, name: str):
    return db.query(models.Pokemon).filter(models.Pokemon.name == name).first()


def get_pokemon_by_id(db: Session, pokemon_id: int):
    return db.query(models.Pokemon).filter(models.Pokemon.id == pokemon_id).first()


def get_pokemon_list(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Pokemon).offset(skip).limit(limit).all()


def create_pokemon(db: Session, pokemon: schemas.PokemonCreate):
    db_pokemon = models.Pokemon(**pokemon.dict())
    db.add(db_pokemon)
    db.commit()
    db.refresh(db_pokemon)
    return db_pokemon


def get_rating_by_pokemon_and_user(db: Session, pokemon_id: int, user_id: str = "admin"):
    return db.query(models.Rating).filter(
        models.Rating.pokemon_id == pokemon_id,
        models.Rating.user_id == user_id
    ).first()


def create_or_update_rating(db: Session, rating: schemas.RatingCreate, user_id: str = "admin"):
    existing_rating = get_rating_by_pokemon_and_user(db, rating.pokemon_id, user_id)
    if existing_rating:
        existing_rating.rating = rating.rating
        existing_rating.comment = rating.comment
        db.commit()
        db.refresh(existing_rating)
        return existing_rating
    db_rating = models.Rating(
        pokemon_id=rating.pokemon_id,
        rating=rating.rating,
        comment=rating.comment,
        user_id=user_id,
    )
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating


def get_pokemon_with_rating(db: Session, pokemon_name: str, user_id: str = "admin"):
    pokemon = get_pokemon_by_name(db, pokemon_name)
    rating = None
    if pokemon:
        rating = get_rating_by_pokemon_and_user(db, pokemon.id, user_id)
    return {"pokemon": pokemon, "rating": rating}


def get_unrated_pokemon(db: Session, limit: int = 10):
    """Get Pokemon that haven't been rated yet."""
    rated_pokemon_ids = db.query(models.Rating.pokemon_id).distinct().all()
    rated_ids = [row[0] for row in rated_pokemon_ids]
    return db.query(models.Pokemon).filter(~models.Pokemon.id.in_(rated_ids)).order_by(func.random()).limit(limit).all()


def search_pokemon(db: Session, query: str, limit: int = 20):
    """Search Pokemon by name."""
    return db.query(models.Pokemon).filter(
        models.Pokemon.name.ilike(f"%{query}%")
    ).limit(limit).all()


# Analytics functions
def get_top_rated_pokemon(db: Session, limit: int = 10):
    """Get top rated Pokemon with names and sprite URLs."""
    results = db.query(
        models.Pokemon.name,
        models.Rating.rating,
        models.Rating.comment,
        models.Pokemon.sprite_url,
        models.Pokemon.artwork_url,
    ).join(models.Pokemon, models.Rating.pokemon_id == models.Pokemon.id)
    results = results.order_by(desc(models.Rating.rating)).limit(limit).all()
    return [
        {
            "pokemon_name": row[0],
            "rating": row[1],
            "comment": row[2],
            "sprite_url": row[3],
            "artwork_url": row[4],
        }
        for row in results
    ]


def get_bottom_rated_pokemon(db: Session, limit: int = 10):
    """Get bottom rated Pokemon with names and sprite URLs."""
    results = db.query(
        models.Pokemon.name,
        models.Rating.rating,
        models.Rating.comment,
        models.Pokemon.sprite_url,
        models.Pokemon.artwork_url,
    ).join(models.Pokemon, models.Rating.pokemon_id == models.Pokemon.id)
    results = results.order_by(asc(models.Rating.rating)).limit(limit).all()
    return [
        {
            "pokemon_name": row[0],
            "rating": row[1],
            "comment": row[2],
            "sprite_url": row[3],
            "artwork_url": row[4],
        }
        for row in results
    ]


def get_ratings_by_type(db: Session, pokemon_type: str):
    """Get average rating for a specific type."""
    results = db.query(
        models.Pokemon.name,
        models.Rating.rating,
        models.Pokemon.sprite_url,
        models.Pokemon.artwork_url,
    ).join(
        models.Pokemon, models.Rating.pokemon_id == models.Pokemon.id
    ).filter(
        (models.Pokemon.type1 == pokemon_type) | (models.Pokemon.type2 == pokemon_type)
    ).all()
    
    # Convert to list of dictionaries
    return [{"pokemon_name": row[0], "rating": row[1], "sprite_url": row[2], "artwork_url": row[3]} for row in results]


def get_ratings_by_generation(db: Session, generation: int):
    """Get ratings for Pokemon from a specific generation."""
    results = db.query(
        models.Pokemon.name,
        models.Rating.rating,
        models.Pokemon.sprite_url,
        models.Pokemon.artwork_url,
    ).join(
        models.Pokemon, models.Rating.pokemon_id == models.Pokemon.id
    ).filter(
        models.Pokemon.generation == generation
    ).all()
    
    # Convert to list of dictionaries
    return [{"pokemon_name": row[0], "rating": row[1], "sprite_url": row[2], "artwork_url": row[3]} for row in results]


def get_rating_statistics(db: Session):
    """Get overall rating statistics."""
    stats = db.query(
        func.count(models.Rating.id).label('total_rated'),
        func.avg(models.Rating.rating).label('average_rating'),
        func.max(models.Rating.rating).label('max_rating'),
        func.min(models.Rating.rating).label('min_rating')
    ).first()
    
    total_pokemon = db.query(func.count(models.Pokemon.id)).scalar()
    
    return {
        'total_pokemon': total_pokemon,
        'total_rated': stats.total_rated,
        'unrated': total_pokemon - stats.total_rated,
        'average_rating': float(stats.average_rating) if stats.average_rating else 0,
        'max_rating': float(stats.max_rating) if stats.max_rating else 0,
        'min_rating': float(stats.min_rating) if stats.min_rating else 0
    }


# User functions
def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    from .auth import get_password_hash
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user