import csv
import sys
import os
import asyncio
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models, crud, schemas
from app.auth import get_password_hash





def import_pokemon_data():
    """Import Pokemon data from CSV."""
    print("Starting Pokemon data import...")
    
    # Ensure data directory exists
    Path("data").mkdir(exist_ok=True)
    
    # Create database tables
    models.Base.metadata.create_all(bind=engine)
    
    # Create admin user
    db = SessionLocal()
    try:
        from app.config import settings
        existing_user = db.query(models.User).filter(models.User.username == settings.admin_username).first()
        if not existing_user:
            hashed_password = get_password_hash(settings.admin_password)
            admin_user = models.User(
                username=settings.admin_username,
                hashed_password=hashed_password,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print(f"Created admin user: {settings.admin_username}")
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()
    
    # Read CSV file
    csv_file = 'Pokemon4Elise.csv'
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        return
    
    # Map regions to generations
    region_to_gen = {
        'Kanto': 1, 'Johto': 2, 'Hoenn': 3, 'Sinnoh': 4,
        'Unova': 5, 'Kalos': 6, 'Alola': 7, 'Galar': 8,
        'Hisui': 8, 'Paldea': 9
    }
    
    db = SessionLocal()
    try:
        pokemon_count = 0
        rating_count = 0
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader)  # Skip header row
            
            for row in reader:
                try:
                    if len(row) < 7:
                        continue
                        
                    dex, region, name, rating, type1, type2, comments = row[:7]
                    
                    # Skip empty names
                    if not name or name.strip() == '':
                        continue
                    
                    name = name.strip()
                    print(f"Processing {name}...")
                    
                    # Get data
                    try:
                        dex_num = int(dex) if dex and dex.strip() else None
                    except ValueError:
                        dex_num = None
                        
                    generation = region_to_gen.get(region, 1)
                    type1 = type1.lower().strip() if type1 and type1.strip() else 'normal'
                    type2 = type2.lower().strip() if type2 and type2.strip() else None
                    
                    # Generate sprite URLs based on dex number
                    sprite_url = None
                    artwork_url = None
                    if dex_num:
                        sprite_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{dex_num}.png"
                        artwork_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{dex_num}.png"
                    
                    # Create Pokemon entry
                    pokemon_data = {
                        'name': name,
                        'dex_number': dex_num,
                        'type1': type1,
                        'type2': type2,
                        'generation': generation,
                        'sprite_url': sprite_url,
                        'artwork_url': artwork_url
                    }
                    
                    # Check if Pokemon already exists
                    existing_pokemon = crud.get_pokemon_by_name(db, name)
                    if not existing_pokemon:
                        pokemon_schema = schemas.PokemonCreate(**pokemon_data)
                        crud.create_pokemon(db, pokemon_schema)
                        pokemon_count += 1
                    
                    # Create rating if it exists
                    if rating and rating.strip():
                        try:
                            rating_value = float(rating)
                            comment = comments.strip() if comments and comments.strip() else None
                            if comment and comment.lower() in ['nan', '']:
                                comment = None
                            
                            rating_data = schemas.RatingCreate(
                                pokemon_name=name,
                                rating=rating_value,
                                comment=comment
                            )
                            crud.create_or_update_rating(db, rating_data)
                            rating_count += 1
                        except ValueError:
                            print(f"Invalid rating for {name}: {rating}")
                    
                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue
        
        print(f"\nImport completed!")
        print(f"Pokemon imported: {pokemon_count}")
        print(f"Ratings imported: {rating_count}")
        
    finally:
        db.close()


if __name__ == "__main__":
    import_pokemon_data()