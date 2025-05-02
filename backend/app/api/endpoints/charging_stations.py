from fastapi import APIRouter, Query, HTTPException
from app.services.charging_service import ChargingService
from app.models.charging import ChargingStationResponse
from typing import Optional

router = APIRouter()

@router.get("", response_model=ChargingStationResponse)
async def get_charging_stations(
    latitude: float = Query(..., description="Latitude of the search center"),
    longitude: float = Query(..., description="Longitude of the search center"),
    radius: float = Query(10.0, description="Search radius in kilometers", ge=0.1, le=50.0),
    connector_type: Optional[str] = Query(None, description="Filter by connector type")
):
    """
    Get charging stations around a specific location.
    """
    charging_service = ChargingService()
    
    try:
        stations = charging_service.get_charging_stations(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            connector_type=connector_type
        )
        return stations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
