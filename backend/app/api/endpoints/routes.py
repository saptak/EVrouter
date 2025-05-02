from fastapi import APIRouter, Depends, HTTPException
from app.services.route_service import RouteService
from app.models.route import RouteRequest, RouteResponse
from typing import List

router = APIRouter()

@router.post("/calculate", response_model=RouteResponse)
async def calculate_route(route_request: RouteRequest):
    """
    Calculate an optimal route with charging stops for an electric vehicle.
    """
    route_service = RouteService()
    
    try:
        route = route_service.calculate_route(
            start=route_request.start,
            destination=route_request.destination,
            waypoints=route_request.waypoints,
            vehicle_range=route_request.vehicle_range
        )
        return route
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
