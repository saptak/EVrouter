from pydantic import BaseModel
from typing import List, Optional
from app.models.location import Location

class ConnectorType(BaseModel):
    id: str
    name: str
    power: float  # in kW
    
class ChargingStation(BaseModel):
    id: str
    name: str
    location: Location
    operator: Optional[str] = None
    connectors: List[ConnectorType]
    available: bool = True
    
class ChargingStationResponse(BaseModel):
    items: List[ChargingStation]
    total: int
