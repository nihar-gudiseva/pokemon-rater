from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PokemonBase(BaseModel):
    name: str
    dex_number: int
    type1: str
    type2: Optional[str] = None
    generation: int


class PokemonCreate(PokemonBase):
    sprite_url: Optional[str] = None
    artwork_url: Optional[str] = None


class Pokemon(PokemonBase):
    id: int
    sprite_url: Optional[str] = None
    artwork_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class RatingBase(BaseModel):
    pokemon_name: str
    rating: float
    comment: Optional[str] = None


class RatingCreate(RatingBase):
    pass


class Rating(RatingBase):
    id: int
    pokemon_id: int
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class PokemonWithRating(BaseModel):
    pokemon: Pokemon
    rating: Optional[Rating] = None