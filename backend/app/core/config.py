import os
from pydantic import BaseSettings, AnyHttpUrl
from typing import List

class Settings(BaseSettings):
    # API configuration
    API_V1_STR: str = "/v1"

    # CORS settings
    ALLOWED_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React frontend
        "http://localhost:3001",  # React frontend (alternative port)
    ]

    # Neo4j settings
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "evrouter")

    # Map API settings
    # Not used currently, using open-meteo api for now instead
    OPENSTREETMAP_API_URL: str = "https://nominatim.openstreetmap.org/search"

    # OPENCHARGEMAP API settings
    # Not integrated yet
    OPENCHARGE_MAP_API_URL: str = "https://api.openchargemap.io/v3/poi"
    OPENCHARGE_MAP_API_KEY: str = os.getenv("OPENCHARGE_MAP_API_KEY")

    # OSRM API settings
    # used in map_service.get_route
    OSRM_API_URL: str = "http://router.project-osrm.org"

    # open-meteo api settings
    # used in geocoding_service.get_location
    OPEN_METEO_API_URL: str = "https://geocoding-api.open-meteo.com/v1/search"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
