import requests
from app.core.config import settings
from app.models.location import Location
from app.models.route import RouteSegment
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class MapService:
    """Service for interacting with mapping APIs"""
    
    def geocode(self, address: str) -> Optional[Location]:
        """
        Convert an address to coordinates.
        
        Args:
            address: Address to geocode
            
        Returns:
            Location with coordinates if successful, None otherwise
        """
        try:
            params = {
                "q": address,
                "format": "json",
                "limit": 1
            }
            
            response = requests.get(settings.OPENSTREETMAP_API_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                result = data[0]
                return Location(
                    latitude=float(result["lat"]),
                    longitude=float(result["lon"]),
                    name=address,
                    address=result.get("display_name")
                )
            
            return None
        except Exception as e:
            logger.error(f"Geocoding error for address {address}: {str(e)}")
            return None
    
    def get_route(
        self, 
        start: Location, 
        destination: Location, 
        waypoints: Optional[List[Location]] = None
    ) -> List[RouteSegment]:
        """
        Get a route from start to destination, optionally via waypoints.
        
        Args:
            start: Starting location
            destination: Destination location
            waypoints: Optional intermediate locations
            
        Returns:
            List of route segments
        """
        if waypoints is None:
            waypoints = []
            
        try:
            # In a real implementation, this would call the OSRM API
            # For now, return a simple route
            return self._get_mock_route(start, destination, waypoints)
        except Exception as e:
            logger.error(f"Error getting route: {str(e)}")
            return []
    
    def _get_mock_route(
        self, 
        start: Location, 
        destination: Location, 
        waypoints: List[Location]
    ) -> List[RouteSegment]:
        """Create a mock route for testing"""
        segments = []
        
        # Create direct segments between all points in order
        all_points = [start] + waypoints + [destination]
        
        for i in range(len(all_points) - 1):
            current = all_points[i]
            next_point = all_points[i + 1]
            
            # Calculate approximate distance
            distance = self._calculate_distance(current, next_point)
            
            # Estimate duration (assuming 60km/h average speed)
            duration = (distance / 60) * 60  # hours to minutes
            
            segments.append(RouteSegment(
                start_location=current,
                end_location=next_point,
                distance=distance,
                duration=duration,
                is_charging_stop=False,
                polyline=self._create_mock_polyline(current, next_point)
            ))
            
        return segments
    
    def _calculate_distance(self, point1: Location, point2: Location) -> float:
        """Calculate distance between two points (kilometers)"""
        # In a real app, this would use the haversine formula
        # For simplicity, we'll use a very rough approximation
        lat_diff = abs(point1.latitude - point2.latitude)
        lon_diff = abs(point1.longitude - point2.longitude)
        
        # Very rough approximation (1 degree ≈ 111km)
        return ((lat_diff ** 2) + (lon_diff ** 2) ** 0.5) * 111
    
    def _create_mock_polyline(self, start: Location, end: Location) -> str:
        """Create a mock polyline for testing"""
        # In a real app, this would be a properly encoded polyline
        # For testing, we'll just return a placeholder string
        return f"mock_polyline_{start.latitude}_{start.longitude}_{end.latitude}_{end.longitude}"
