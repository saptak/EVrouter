from fastapi import APIRouter, Query, HTTPException
from app.services.geocoding_service import GeocodingService
from app.models import Location

router = APIRouter()

@router.get("", response_model=Location)
async def geocode_location(
    city: str = Query(..., description="City name to geocode")
):
    """
    Geocode a city name to get its coordinates.
    """
    geocoding_service = GeocodingService()
    
    try:
        location = geocoding_service.get_location(city)
        return location
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 