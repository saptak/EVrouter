import os
from pydantic import BaseSettings, AnyHttpUrl
from typing import List, Union

class Settings(BaseSettings):
    # API configuration
    API_V1_STR: str = "/v1"
    
    # CORS settings
    ALLOWED_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React frontend
    ]
    
    # Neo4j settings
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "evrouter")
    
    # Map API settings
    OPENSTREETMAP_API_URL: str = "https://nominatim.openstreetmap.org/search"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
