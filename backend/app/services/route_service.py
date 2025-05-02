from app.db.neo4j import db
from app.models.route import RouteResponse, RouteSegment, ChargingStop
from app.models.location import Location
from app.services.charging_service import ChargingService
from app.services.map_service import MapService
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class RouteService:
    def __init__(self):
        self.charging_service = ChargingService()
        self.map_service = MapService()
    
    def calculate_route(
        self, 
        start: Location, 
        destination: Location, 
        waypoints: Optional[List[Location]] = None,
        vehicle_range: float = 300.0
    ) -> RouteResponse:
        """
        Calculate a route with optimal charging stops.
        
        Args:
            start: Starting location
            destination: Destination location
            waypoints: Optional intermediate locations
            vehicle_range: Vehicle range in kilometers
            
        Returns:
            RouteResponse with complete route including charging stops
        """
        if waypoints is None:
            waypoints = []
            
        logger.info(f"Calculating route from {start.name} to {destination.name} with range {vehicle_range}km")
        
        # 1. Get basic route without charging considerations
        basic_route = self._get_basic_route(start, destination, waypoints)
        
        # 2. Analyze route for range limitations
        segments_with_range = self._analyze_range(basic_route, vehicle_range)
        
        # 3. Insert charging stops where needed
        final_route = self._insert_charging_stops(segments_with_range, vehicle_range)
        
        # 4. Calculate charging times and levels
        route_with_charging = self._calculate_charging_requirements(final_route)
        
        # 5. Prepare response
        return RouteResponse(
            route_segments=route_with_charging,
            total_distance=sum(segment.distance for segment in route_with_charging),
            total_duration=sum(segment.duration for segment in route_with_charging),
            charging_stops=self._extract_charging_stops(route_with_charging)
        )
    
    def _get_basic_route(
        self, 
        start: Location, 
        destination: Location,
        waypoints: Optional[List[Location]] = None
    ) -> List[RouteSegment]:
        """Get the basic route from map service without considering charging"""
        if waypoints is None:
            waypoints = []
            
        try:
            # Use Neo4j for path finding if locations are already in the database
            with db.get_session() as session:
                # In a real implementation, this would use Neo4j's graph algorithms
                # For now, we'll use the map service as a fallback
                pass
                
            # Use map service to get the route
            return self.map_service.get_route(start, destination, waypoints)
            
        except Exception as e:
            logger.error(f"Failed to get basic route: {str(e)}")
            # Fallback to simplified route calculation
            return self._create_simplified_route(start, destination, waypoints)
    
    def _create_simplified_route(
        self,
        start: Location,
        destination: Location,
        waypoints: List[Location]
    ) -> List[RouteSegment]:
        """Create a simplified route for testing purposes"""
        segments = []
        
        # Create direct segments between all points in order
        all_points = [start] + waypoints + [destination]
        
        for i in range(len(all_points) - 1):
            current = all_points[i]
            next_point = all_points[i + 1]
            
            # Calculate approximate distance (in a real app, this would use actual road distances)
            distance = self._calculate_straight_distance(current, next_point)
            
            # Estimate duration (assuming 60km/h average speed)
            duration = (distance / 60) * 60  # hours to minutes
            
            segments.append(RouteSegment(
                start_location=current,
                end_location=next_point,
                distance=distance,
                duration=duration,
                is_charging_stop=False,
                polyline=None  # In a real app, this would be an encoded polyline
            ))
            
        return segments
    
    def _calculate_straight_distance(self, point1: Location, point2: Location) -> float:
        """Calculate straight-line distance between two points (kilometers)"""
        # In a real app, this would use the haversine formula
        # For simplicity, we'll use a very rough approximation
        lat_diff = abs(point1.latitude - point2.latitude)
        lon_diff = abs(point1.longitude - point2.longitude)
        
        # Very rough approximation (1 degree ≈ 111km)
        return ((lat_diff ** 2) + (lon_diff ** 2) ** 0.5) * 111
    
    def _analyze_range(
        self, 
        route_segments: List[RouteSegment], 
        vehicle_range: float
    ) -> List[RouteSegment]:
        """
        Analyze route segments against vehicle range.
        Add a range_sufficient boolean property to each segment.
        """
        remaining_range = vehicle_range
        analyzed_segments = []
        
        for segment in route_segments:
            # Check if the current segment can be completed with remaining range
            range_sufficient = segment.distance <= remaining_range
            
            # Create a copy of the segment with range information
            segment_copy = segment.dict()
            segment_copy["range_sufficient"] = range_sufficient
            
            # Calculate remaining range after this segment
            if range_sufficient:
                remaining_range -= segment.distance
            
            analyzed_segments.append(RouteSegment(**segment_copy))
            
        return analyzed_segments
    
    def _insert_charging_stops(
        self, 
        route_segments: List[RouteSegment], 
        vehicle_range: float
    ) -> List[RouteSegment]:
        """Insert charging stops where needed based on range analysis"""
        final_route = []
        remaining_range = vehicle_range
        
        for segment in route_segments:
            if segment.distance <= remaining_range:
                # We can drive this segment without charging
                final_route.append(segment)
                remaining_range -= segment.distance
            else:
                # Need a charging stop before this segment
                charging_station = self._find_nearest_charging_station(segment.start_location)
                
                # Add a charging stop segment
                charging_segment = RouteSegment(
                    start_location=segment.start_location,
                    end_location=charging_station,
                    distance=0,  # No additional distance for charging
                    duration=0,  # Will be filled in by _calculate_charging_requirements
                    is_charging_stop=True,
                    charging_time=None,  # Will be filled in later
                    charge_to_level=None  # Will be filled in later
                )
                
                final_route.append(charging_segment)
                
                # After charging, we can continue with the original segment
                final_route.append(segment)
                remaining_range = vehicle_range - segment.distance
                
        return final_route
    
    def _find_nearest_charging_station(self, location: Location) -> Location:
        """Find the nearest charging station to a given location"""
        # In a real app, this would query the Neo4j database for nearby charging stations
        # For simplicity, we'll create a simulated charging station at the same location
        return Location(
            latitude=location.latitude,
            longitude=location.longitude,
            name=f"Charging Station near {location.name or 'location'}",
            address="123 Charge St"
        )
    
    def _calculate_charging_requirements(
        self, 
        route_segments: List[RouteSegment]
    ) -> List[RouteSegment]:
        """Calculate required charging time and level for each stop"""
        for i, segment in enumerate(route_segments):
            if segment.is_charging_stop:
                # Get the upcoming segment after charging
                next_segment_index = i + 1
                
                if next_segment_index < len(route_segments):
                    next_segment = route_segments[next_segment_index]
                    
                    # Calculate required charge level (% of full range needed for next segment)
                    charge_to_level = min(100, (next_segment.distance / 300) * 100 + 20)
                    
                    # Calculate charging time (simplified model: 20% per 15 minutes)
                    charging_time = (charge_to_level / 20) * 15
                    
                    # Update the segment with charging requirements
                    updated_segment = segment.dict()
                    updated_segment["charging_time"] = charging_time
                    updated_segment["charge_to_level"] = charge_to_level
                    updated_segment["duration"] = charging_time  # Add charging time to segment duration
                    
                    route_segments[i] = RouteSegment(**updated_segment)
                    
        return route_segments
    
    def _extract_charging_stops(
        self, 
        route_segments: List[RouteSegment]
    ) -> List[ChargingStop]:
        """Extract charging stops from the route for summary view"""
        charging_stops = []
        for segment in route_segments:
            if segment.is_charging_stop and segment.charging_time is not None and segment.charge_to_level is not None:
                charging_stops.append(ChargingStop(
                    location=segment.end_location,
                    charging_time=segment.charging_time,
                    charge_to_level=segment.charge_to_level
                ))
        return charging_stops
