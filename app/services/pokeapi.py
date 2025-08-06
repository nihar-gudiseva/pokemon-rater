import httpx
from typing import Optional, Dict, Any
from ..config import settings


class PokeAPIService:
    def __init__(self):
        self.base_url = settings.pokeapi_base_url
        
    async def get_pokemon_by_name(self, name: str) -> Optional[Dict[Any, Any]]:
        """Fetch Pokemon data from PokeAPI by name."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/pokemon/{name.lower()}")
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception as e:
                print(f"Error fetching Pokemon {name}: {e}")
                return None
    
    async def get_pokemon_species(self, name: str) -> Optional[Dict[Any, Any]]:
        """Fetch Pokemon species data for generation info."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/pokemon-species/{name.lower()}")
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception as e:
                print(f"Error fetching Pokemon species {name}: {e}")
                return None
    
    async def get_generation_number(self, generation_url: str) -> int:
        """Extract generation number from generation URL."""
        try:
            # URL format: https://pokeapi.co/api/v2/generation/1/
            return int(generation_url.split('/')[-2])
        except:
            return 1  # Default to generation 1
    
    async def get_pokemon_complete_data(self, name: str) -> Optional[Dict[str, Any]]:
        """Get complete Pokemon data including generation."""
        pokemon_data = await self.get_pokemon_by_name(name)
        if not pokemon_data:
            return None
            
        species_data = await self.get_pokemon_species(name)
        generation = 1
        if species_data and 'generation' in species_data:
            generation = await self.get_generation_number(species_data['generation']['url'])
        
        # Extract types
        types = []
        for type_info in pokemon_data.get('types', []):
            types.append(type_info['type']['name'])
        
        return {
            'name': pokemon_data['name'].title(),
            'dex_number': pokemon_data['id'],
            'type1': types[0] if len(types) > 0 else 'normal',
            'type2': types[1] if len(types) > 1 else None,
            'generation': generation,
            'sprite_url': pokemon_data['sprites']['front_default'],
            'artwork_url': pokemon_data['sprites']['other']['official-artwork']['front_default']
        }


pokeapi_service = PokeAPIService()