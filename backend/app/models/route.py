from pydantic import BaseModel
from typing import List, Optional
from app.models.location import Location

class RouteRequest(BaseModel):
    start: Location
    destination: Location
    waypoints: Optional[List[Location]] = []
    vehicle_range: float = 300.0  # in kilometers

class RouteSegment(BaseModel):
    start_location: Location
    end_location: Location
    distance: float  # in kilometers
    duration: float  # in minutes
    is_charging_stop: bool = False
    charging_time: Optional[float] = None  # in minutes
    charge_to_level: Optional[float] = None  # percentage
    polyline: Optional[str] = None  # encoded polyline for map rendering

class ChargingStop(BaseModel):
    location: Location
    charging_time: float  # in minutes
    charge_to_level: float  # percentage

class RouteResponse(BaseModel):
    route_segments: List[RouteSegment]
    total_distance: float  # in kilometers
    total_duration: float  # in minutes
    charging_stops: List[ChargingStop]
