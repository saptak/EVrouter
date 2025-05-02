from app.db.neo4j import db
from app.models.charging import ChargingStation, ChargingStationResponse, ConnectorType
from app.models.location import Location
from typing import List, Optional

class ChargingService:
    def get_charging_stations(
        self,
        latitude: float,
        longitude: float,
        radius: float = 10.0,
        connector_type: Optional[str] = None
    ) -> ChargingStationResponse:
        """
        Get charging stations around a specific location.
        
        Args:
            latitude: Latitude of the search center
            longitude: Longitude of the search center
            radius: Search radius in kilometers
            connector_type: Optional filter by connector type
            
        Returns:
            ChargingStationResponse with matching charging stations
        """
        try:
            with db.get_session() as session:
                # In a real implementation, this would query Neo4j
                # For now, return mock data
                return self._get_mock_charging_stations(latitude, longitude, radius, connector_type)
        except Exception as e:
            # Log the error
            print(f"Error getting charging stations: {str(e)}")
            return ChargingStationResponse(items=[], total=0)
    
    def _get_mock_charging_stations(
        self,
        latitude: float,
        longitude: float,
        radius: float,
        connector_type: Optional[str]
    ) -> ChargingStationResponse:
        """Generate mock charging stations for testing"""
        # Create some variation in the locations
        offsets = [
            (0.01, 0.01),
            (-0.01, 0.02),
            (0.02, -0.01),
            (-0.02, -0.02),
            (0.03, 0.03)
        ]
        
        stations = []
        
        for i, (lat_offset, lon_offset) in enumerate(offsets):
            station_location = Location(
                latitude=latitude + lat_offset,
                longitude=longitude + lon_offset,
                name=f"EV Charging Station {i+1}",
                address=f"{i+1} Charging Avenue"
            )
            
            # Create connectors
            connectors = [
                ConnectorType(id="ccs", name="CCS", power=150.0),
                ConnectorType(id="chademo", name="CHAdeMO", power=100.0),
                ConnectorType(id="type2", name="Type 2", power=22.0)
            ]
            
            # Filter by connector type if specified
            if connector_type:
                connectors = [c for c in connectors if c.id == connector_type]
                if not connectors:
                    continue
            
            station = ChargingStation(
                id=f"station-{i+1}",
                name=f"EV Charging Station {i+1}",
                location=station_location,
                operator="EVrouter Network",
                connectors=connectors,
                available=True
            )
            
            stations.append(station)
        
        return ChargingStationResponse(
            items=stations,
            total=len(stations)
        )
