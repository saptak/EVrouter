import logging
import requests
from typing import List, Optional
from app.core.config import settings
from app.models import Location, RouteSegment
from app.services.geocoding_service import GeocodingService

logger = logging.getLogger(__name__)

class MapService:
    """Service for interacting with mapping APIs"""
    
    def geocode(self, address: str) -> Optional[Location]:
        # implement later
        # use open-meteo geocoding api for now
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
        Get a route from start to destination, optionally via waypoints using OSRM API.
        
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
            # Format coordinates for OSRM (lon,lat format)
            coords = [f"{start.longitude},{start.latitude}"]
            
            # Add waypoints
            for point in waypoints:
                coords.append(f"{point.longitude},{point.latitude}")
                
            # Add destination
            coords.append(f"{destination.longitude},{destination.latitude}")
            
            # Build OSRM API URL
            coordinates = ";".join(coords)
            url = f"{settings.OSRM_API_URL}/route/v1/driving/{coordinates}"
            
            # Parameters for the request
            params = {
                "overview": "full",  # Get full geometry
                "steps": "true",     # Get turn-by-turn instructions
                "annotations": "true" # Get additional data like duration and distance
            }
            
            # Make request to OSRM
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data["code"] != "Ok":
                logger.error(f"OSRM API error: {data['message'] if 'message' in data else 'Unknown error'}")
                return []
            
            # Process the route into segments
            return self._process_osrm_response(data, [start] + waypoints + [destination])
            
        except Exception as e:
            logger.error(f"Error getting route from OSRM: {str(e)}")
            return []
    
    def _process_osrm_response(self, data: dict, locations: List[Location]) -> List[RouteSegment]:
        """Process OSRM response into route segments"""
        segments = []
        route = data["routes"][0]  # Get the first (best) route
        
        # Process each leg of the journey
        for i, leg in enumerate(route["legs"]):
            start_location = locations[i]
            end_location = locations[i + 1]
            
            segments.append(RouteSegment(
                start_location=start_location,
                end_location=end_location,
                distance=leg["distance"] / 1000,  # Convert to kilometers
                duration=leg["duration"] / 60,    # Convert to minutes
                is_charging_stop=False,
                polyline=route["geometry"]  # OSRM returns encoded polyline
            ))
        
        return segments

if __name__ == "__main__":
    map_service = MapService()
    geocoding_service = GeocodingService()
    seattle = geocoding_service.get_location("Seattle")
    redmond = geocoding_service.get_location("Redmond")
    start = seattle
    destination = redmond
    waypoints = []
    route = map_service.get_route(start, destination, waypoints)
    print(route)