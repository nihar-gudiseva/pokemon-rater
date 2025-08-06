from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base


class Pokemon(Base):
    __tablename__ = "pokemon"
    
    id = Column(Integer, primary_key=True, index=True)
    dex_number = Column(Integer, unique=True, index=True)
    name = Column(String, unique=True, index=True)
    type1 = Column(String, index=True)
    type2 = Column(String, nullable=True, index=True)
    generation = Column(Integer, index=True)
    sprite_url = Column(String, nullable=True)
    artwork_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    pokemon_id = Column(Integer, index=True)  # References Pokemon.id
    pokemon_name = Column(String, index=True)  # For easier queries
    rating = Column(Float)
    comment = Column(Text, nullable=True)
    user_id = Column(String, default="admin")  # For future multi-user support
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())