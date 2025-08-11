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


def get_rating_by_pokemon_name(db: Session, pokemon_name: str):
    return db.query(models.Rating).filter(models.Rating.pokemon_name == pokemon_name).first()


def create_or_update_rating(db: Session, rating: schemas.RatingCreate):
    # Check if rating already exists
    existing_rating = get_rating_by_pokemon_name(db, rating.pokemon_name)
    
    if existing_rating:
        # Update existing rating
        existing_rating.rating = rating.rating
        existing_rating.comment = rating.comment
        db.commit()
        db.refresh(existing_rating)
        return existing_rating
    else:
        # Create new rating
        pokemon = get_pokemon_by_name(db, rating.pokemon_name)
        db_rating = models.Rating(
            pokemon_id=pokemon.id if pokemon else None,
            pokemon_name=rating.pokemon_name,
            rating=rating.rating,
            comment=rating.comment
        )
        db.add(db_rating)
        db.commit()
        db.refresh(db_rating)
        return db_rating


def get_pokemon_with_rating(db: Session, pokemon_name: str):
    pokemon = get_pokemon_by_name(db, pokemon_name)
    rating = get_rating_by_pokemon_name(db, pokemon_name)
    return {"pokemon": pokemon, "rating": rating}


def get_unrated_pokemon(db: Session, limit: int = 10):
    """Get Pokemon that haven't been rated yet."""
    rated_pokemon_names = db.query(models.Rating.pokemon_name).distinct().all()
    rated_names = [name[0] for name in rated_pokemon_names]
    return db.query(models.Pokemon).filter(
        ~models.Pokemon.name.in_(rated_names)
    ).order_by(func.random()).limit(limit).all()


def search_pokemon(db: Session, query: str, limit: int = 20):
    """Search Pokemon by name."""
    return db.query(models.Pokemon).filter(
        models.Pokemon.name.ilike(f"%{query}%")
    ).limit(limit).all()


# Analytics functions
def get_top_rated_pokemon(db: Session, limit: int = 10):
    """Get top rated Pokemon."""
    return db.query(models.Rating).order_by(desc(models.Rating.rating)).limit(limit).all()


def get_bottom_rated_pokemon(db: Session, limit: int = 10):
    """Get bottom rated Pokemon."""
    return db.query(models.Rating).order_by(asc(models.Rating.rating)).limit(limit).all()


def get_ratings_by_type(db: Session, pokemon_type: str):
    """Get average rating for a specific type."""
    results = db.query(
        models.Rating.pokemon_name,
        models.Rating.rating
    ).join(
        models.Pokemon, models.Rating.pokemon_name == models.Pokemon.name
    ).filter(
        (models.Pokemon.type1 == pokemon_type) | (models.Pokemon.type2 == pokemon_type)
    ).all()
    
    # Convert to list of dictionaries
    return [{"pokemon_name": row[0], "rating": row[1]} for row in results]


def get_ratings_by_generation(db: Session, generation: int):
    """Get ratings for Pokemon from a specific generation."""
    results = db.query(
        models.Rating.pokemon_name,
        models.Rating.rating
    ).join(
        models.Pokemon, models.Rating.pokemon_name == models.Pokemon.name
    ).filter(
        models.Pokemon.generation == generation
    ).all()
    
    # Convert to list of dictionaries
    return [{"pokemon_name": row[0], "rating": row[1]} for row in results]


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