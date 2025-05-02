# EVrouter Implementation Documentation

This document provides detailed technical implementation guidelines for the EVrouter application, with a focus on modular design principles.

## Table of Contents
1. [Project Structure](#project-structure)
2. [Backend Implementation](#backend-implementation)
3. [Frontend Implementation](#frontend-implementation)
4. [Integration and Data Flow](#integration-and-data-flow)
5. [Development and Testing](#development-and-testing)

## Project Structure

The EVrouter application follows a modular architecture with clear separation of concerns:

```
EVrouter/
├── backend/               # Python backend
│   ├── app/               # Main application
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core business logic
│   │   ├── db/            # Database interactions
│   │   ├── models/        # Data models
│   │   ├── services/      # Service layer
│   │   └── utils/         # Utility functions
│   ├── tests/             # Backend tests
│   ├── config.py          # Configuration
│   ├── main.py            # Application entry point
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend
│   ├── public/            # Static assets
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── common/    # Shared components
│   │   │   ├── map/       # Map-related components
│   │   │   ├── routing/   # Route-related components
│   │   │   └── charging/  # Charging station components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # Frontend services
│   │   ├── utils/         # Utility functions
│   │   ├── contexts/      # React contexts
│   │   ├── types/         # TypeScript type definitions
│   │   ├── App.tsx        # Main application component
│   │   └── index.tsx      # Entry point
│   ├── package.json       # Node dependencies
│   └── tsconfig.json      # TypeScript configuration
├── docker-compose.yml     # Docker services configuration
├── README.md              # Project documentation
└── .env                   # Environment variables
```

## Backend Implementation

### Setting Up Neo4j Database

We use Neo4j to store and query road networks and charging station data. This graph database is ideal for route planning as it efficiently handles complex path finding.

#### Docker Configuration for Neo4j

```yaml
# docker-compose.yml (excerpt for Neo4j)
version: '3.8'

services:
  neo4j:
    image: neo4j:4.4
    ports:
      - "7474:7474"  # Browser interface
      - "7687:7687"  # Bolt protocol
    environment:
      - NEO4J_AUTH=neo4j/evrouter
      - NEO4J_dbms_memory_heap_max__size=2G
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - neo4j_import:/var/lib/neo4j/import
    networks:
      - evrouter-network

volumes:
  neo4j_data:
  neo4j_logs:
  neo4j_import:

networks:
  evrouter-network:
    driver: bridge
```

### Backend API with FastAPI

The backend is built with FastAPI for its performance, automatic documentation, and ease of use.

#### Main Application Entry Point

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import api_router
from app.core.config import settings

app = FastAPI(
    title="EVrouter API",
    description="API for electric vehicle route planning with charging stations",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

#### Configuration Management

```python
# backend/app/core/config.py
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
```

#### Neo4j Database Connector

```python
# backend/app/db/neo4j.py
from neo4j import GraphDatabase
from app.core.config import settings
from contextlib import contextmanager

class Neo4jDatabase:
    def __init__(self):
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self._driver = None

    def connect(self):
        if not self._driver:
            self._driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
        return self._driver

    def close(self):
        if self._driver:
            self._driver.close()
            self._driver = None

    @contextmanager
    def get_session(self):
        driver = self.connect()
        session = driver.session()
        try:
            yield session
        finally:
            session.close()

# Singleton instance
db = Neo4jDatabase()
```

#### API Routes

```python
# backend/app/api/routes.py
from fastapi import APIRouter
from app.api.endpoints import routes, charging_stations

api_router = APIRouter()
api_router.include_router(routes.router, prefix="/routes", tags=["routes"])
api_router.include_router(charging_stations.router, prefix="/charging-stations", tags=["charging-stations"])
```

#### Route Endpoints

```python
# backend/app/api/endpoints/routes.py
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
```

#### Route Service

```python
# backend/app/services/route_service.py
from app.db.neo4j import db
from app.models.route import RouteResponse, RouteSegment, ChargingStop
from app.models.location import Location
from app.services.charging_service import ChargingService
from app.services.map_service import MapService
from typing import List, Optional

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
            vehicle_range: Vehicle range in kilometers/miles
            
        Returns:
            RouteResponse with complete route including charging stops
        """
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
        # Use Neo4j for path finding
        with db.get_session() as session:
            # Implementation will use Neo4j's graph algorithms
            # This is a simplified placeholder
            pass
        
        # For now, return a mock route
        return self.map_service.get_route(start, destination, waypoints)
    
    def _analyze_range(
        self, 
        route_segments: List[RouteSegment], 
        vehicle_range: float
    ) -> List[RouteSegment]:
        """Analyze route segments against vehicle range"""
        # Implementation for range analysis
        pass
    
    def _insert_charging_stops(
        self, 
        route_segments: List[RouteSegment], 
        vehicle_range: float
    ) -> List[RouteSegment]:
        """Insert charging stops where needed based on range analysis"""
        # Implementation to find and insert charging stops
        pass
    
    def _calculate_charging_requirements(
        self, 
        route_segments: List[RouteSegment]
    ) -> List[RouteSegment]:
        """Calculate required charging time and level for each stop"""
        # Implementation for charging calculations
        pass
    
    def _extract_charging_stops(
        self, 
        route_segments: List[RouteSegment]
    ) -> List[ChargingStop]:
        """Extract charging stops from the route for summary view"""
        charging_stops = []
        for segment in route_segments:
            if segment.is_charging_stop:
                charging_stops.append(ChargingStop(
                    location=segment.end_location,
                    charging_time=segment.charging_time,
                    charge_to_level=segment.charge_to_level
                ))
        return charging_stops
```

#### Data Models

```python
# backend/app/models/location.py
from pydantic import BaseModel
from typing import Optional

class Location(BaseModel):
    latitude: float
    longitude: float
    name: Optional[str] = None
    address: Optional[str] = None
```

```python
# backend/app/models/route.py
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
```

## Frontend Implementation

### React Application Setup

We'll use Create React App with TypeScript for the frontend.

#### Project Setup

```bash
npx create-react-app frontend --template typescript
cd frontend
npm install @shadcn/ui leaflet react-leaflet axios
```

#### App Component

```tsx
// frontend/src/App.tsx
import React from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import Layout from './components/common/Layout';
import RouteController from './components/routing/RouteController';

function App() {
  return (
    <ThemeProvider>
      <Layout>
        <RouteController />
      </Layout>
    </ThemeProvider>
  );
}

export default App;
```

#### Layout Component

```tsx
// frontend/src/components/common/Layout.tsx
import React, { ReactNode } from 'react';

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-background">
      <header className="bg-primary text-white p-4 shadow-md">
        <div className="container mx-auto">
          <h1 className="text-2xl font-bold">EVrouter</h1>
        </div>
      </header>
      <main className="container mx-auto p-4">
        {children}
      </main>
      <footer className="bg-accent p-4 mt-8">
        <div className="container mx-auto text-center text-sm">
          &copy; {new Date().getFullYear()} EVrouter - Electric Vehicle Route Planner
        </div>
      </footer>
    </div>
  );
};

export default Layout;
```

#### Route Controller

```tsx
// frontend/src/components/routing/RouteController.tsx
import React, { useState } from 'react';
import RouteForm from './RouteForm';
import MapView from '../map/MapView';
import RouteList from './RouteList';
import { RouteResponse } from '../../types/route';
import { useRouteCalculation } from '../../hooks/useRouteCalculation';

const RouteController: React.FC = () => {
  const [route, setRoute] = useState<RouteResponse | null>(null);
  const { calculateRoute, loading, error } = useRouteCalculation();
  
  const handleRouteCalculation = async (formData: any) => {
    const result = await calculateRoute(formData);
    if (result) {
      setRoute(result);
    }
  };
  
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div className="lg:col-span-1">
        <RouteForm onSubmit={handleRouteCalculation} isLoading={loading} />
        {error && (
          <div className="mt-4 p-3 bg-red-100 text-red-800 rounded">
            {error}
          </div>
        )}
      </div>
      <div className="lg:col-span-2">
        <div className="h-[500px] mb-4">
          <MapView route={route} />
        </div>
        {route && <RouteList route={route} />}
      </div>
    </div>
  );
};

export default RouteController;
```

#### Route Form Component

```tsx
// frontend/src/components/routing/RouteForm.tsx
import React, { useState } from 'react';
import { Button } from '../common/Button';
import { Input } from '../common/Input';
import { Slider } from '../common/Slider';

interface RouteFormProps {
  onSubmit: (formData: any) => void;
  isLoading: boolean;
}

const RouteForm: React.FC<RouteFormProps> = ({ onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    start: '',
    destination: '',
    waypoints: [] as string[],
    vehicleRange: 300,
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleRangeChange = (value: number) => {
    setFormData((prev) => ({
      ...prev,
      vehicleRange: value,
    }));
  };

  const handleAddWaypoint = () => {
    setFormData((prev) => ({
      ...prev,
      waypoints: [...prev.waypoints, ''],
    }));
  };

  const handleWaypointChange = (index: number, value: string) => {
    const updatedWaypoints = [...formData.waypoints];
    updatedWaypoints[index] = value;
    setFormData((prev) => ({
      ...prev,
      waypoints: updatedWaypoints,
    }));
  };

  const handleRemoveWaypoint = (index: number) => {
    const updatedWaypoints = formData.waypoints.filter((_, i) => i !== index);
    setFormData((prev) => ({
      ...prev,
      waypoints: updatedWaypoints,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-4 rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Plan Your EV Route</h2>
      
      <div className="mb-4">
        <label htmlFor="start" className="block text-sm font-medium mb-1">
          Start Location
        </label>
        <Input
          id="start"
          name="start"
          value={formData.start}
          onChange={handleInputChange}
          placeholder="Enter start location"
          required
        />
      </div>
      
      <div className="mb-4">
        <label htmlFor="destination" className="block text-sm font-medium mb-1">
          Destination
        </label>
        <Input
          id="destination"
          name="destination"
          value={formData.destination}
          onChange={handleInputChange}
          placeholder="Enter destination"
          required
        />
      </div>
      
      {formData.waypoints.map((waypoint, index) => (
        <div key={index} className="mb-4 flex items-center">
          <div className="flex-grow">
            <label className="block text-sm font-medium mb-1">
              Waypoint {index + 1}
            </label>
            <Input
              value={waypoint}
              onChange={(e) => handleWaypointChange(index, e.target.value)}
              placeholder={`Enter waypoint ${index + 1}`}
            />
          </div>
          <Button
            type="button"
            onClick={() => handleRemoveWaypoint(index)}
            className="ml-2 mt-5"
            variant="destructive"
            size="sm"
          >
            Remove
          </Button>
        </div>
      ))}
      
      <Button
        type="button"
        onClick={handleAddWaypoint}
        className="mb-4"
        variant="outline"
        size="sm"
      >
        Add Waypoint
      </Button>
      
      <div className="mb-6">
        <label htmlFor="vehicleRange" className="block text-sm font-medium mb-1">
          Vehicle Range: {formData.vehicleRange} km
        </label>
        <Slider
          id="vehicleRange"
          min={100}
          max={800}
          step={10}
          value={[formData.vehicleRange]}
          onValueChange={(values) => handleRangeChange(values[0])}
        />
      </div>
      
      <Button type="submit" disabled={isLoading} className="w-full">
        {isLoading ? 'Calculating Route...' : 'Calculate Route'}
      </Button>
    </form>
  );
};

export default RouteForm;
```

#### Map View Component

```tsx
// frontend/src/components/map/MapView.tsx
import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { RouteResponse } from '../../types/route';
import { decodePolyline } from '../../utils/mapUtils';

interface MapViewProps {
  route: RouteResponse | null;
}

const MapView: React.FC<MapViewProps> = ({ route }) => {
  const [center, setCenter] = useState<[number, number]>([51.505, -0.09]);
  const [zoom, setZoom] = useState(13);
  
  useEffect(() => {
    if (route && route.route_segments.length > 0) {
      // Set map view to start location
      const startLocation = route.route_segments[0].start_location;
      setCenter([startLocation.latitude, startLocation.longitude]);
      setZoom(10);
    }
  }, [route]);
  
  return (
    <MapContainer 
      center={center} 
      zoom={zoom} 
      style={{ height: '100%', width: '100%' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      
      {route && route.route_segments.map((segment, index) => {
        // Decode polyline for the segment
        const positions = segment.polyline 
          ? decodePolyline(segment.polyline)
          : [];
        
        return (
          <React.Fragment key={index}>
            {/* Start location marker */}
            {index === 0 && (
              <Marker position={[segment.start_location.latitude, segment.start_location.longitude]}>
                <Popup>
                  <strong>Start:</strong> {segment.start_location.name || 'Starting Point'}
                </Popup>
              </Marker>
            )}
            
            {/* End location marker */}
            <Marker position={[segment.end_location.latitude, segment.end_location.longitude]}>
              <Popup>
                {segment.is_charging_stop ? (
                  <div>
                    <strong>Charging Stop:</strong> {segment.end_location.name || 'Charging Station'}<br />
                    <strong>Charging Time:</strong> {segment.charging_time} minutes<br />
                    <strong>Charge to:</strong> {segment.charge_to_level}%
                  </div>
                ) : (
                  <strong>{segment.end_location.name || 'Waypoint'}</strong>
                )}
              </Popup>
            </Marker>
            
            {/* Route line */}
            {positions.length > 0 && (
              <Polyline 
                positions={positions}
                color={segment.is_charging_stop ? 'green' : 'blue'}
                weight={4}
              />
            )}
          </React.Fragment>
        );
      })}
    </MapContainer>
  );
};

export default MapView;
```

#### Route List Component

```tsx
// frontend/src/components/routing/RouteList.tsx
import React from 'react';
import { RouteResponse, RouteSegment } from '../../types/route';

interface RouteListProps {
  route: RouteResponse;
}

const RouteList: React.FC<RouteListProps> = ({ route }) => {
  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Route Details</h2>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <span className="text-sm text-gray-500">Total Distance</span>
          <p className="text-lg font-medium">{route.total_distance.toFixed(1)} km</p>
        </div>
        <div>
          <span className="text-sm text-gray-500">Total Duration</span>
          <p className="text-lg font-medium">
            {Math.floor(route.total_duration / 60)}h {Math.round(route.total_duration % 60)}m
          </p>
        </div>
        <div>
          <span className="text-sm text-gray-500">Charging Stops</span>
          <p className="text-lg font-medium">{route.charging_stops.length}</p>
        </div>
        <div>
          <span className="text-sm text-gray-500">Total Charging Time</span>
          <p className="text-lg font-medium">
            {Math.floor(route.charging_stops.reduce((sum, stop) => sum + stop.charging_time, 0) / 60)}h {Math.round(route.charging_stops.reduce((sum, stop) => sum + stop.charging_time, 0) % 60)}m
          </p>
        </div>
      </div>
      
      <div className="border-t pt-4">
        <h3 className="text-lg font-medium mb-2">Route Segments</h3>
        
        <div className="space-y-4">
          {route.route_segments.map((segment, index) => (
            <RouteSegmentItem key={index} segment={segment} index={index} />
          ))}
        </div>
      </div>
    </div>
  );
};

interface RouteSegmentItemProps {
  segment: RouteSegment;
  index: number;
}

const RouteSegmentItem: React.FC<RouteSegmentItemProps> = ({ segment, index }) => {
  return (
    <div className={`p-3 rounded ${segment.is_charging_stop ? 'bg-green-50' : 'bg-gray-50'}`}>
      <div className="flex items-center mb-2">
        <div className="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center mr-2">
          {index + 1}
        </div>
        <div>
          <h4 className="font-medium">
            {segment.start_location.name || 'Unknown'} → {segment.end_location.name || 'Unknown'}
          </h4>
        </div>
      </div>
      
      <div className="ml-10">
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <span className="text-gray-500">Distance:</span> {segment.distance.toFixed(1)} km
          </div>
          <div>
            <span className="text-gray-500">Duration:</span> {Math.floor(segment.duration / 60)}h {Math.round(segment.duration % 60)}m
          </div>
        </div>
        
        {segment.is_charging_stop && (
          <div className="mt-2 p-2 bg-green-100 rounded text-sm">
            <div className="font-medium text-green-800 mb-1">Charging Stop</div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="text-gray-600">Charging Time:</span> {segment.charging_time} min
              </div>
              <div>
                <span className="text-gray-600">Charge to:</span> {segment.charge_to_level}%
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RouteList;
```

#### Custom Hook for Route Calculation

```tsx
// frontend/src/hooks/useRouteCalculation.ts
import { useState } from 'react';
import { RouteRequest, RouteResponse } from '../types/route';
import { routeService } from '../services/routeService';

export const useRouteCalculation = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const calculateRoute = async (formData: any): Promise<RouteResponse | null> => {
    setLoading(true);
    setError(null);
    
    try {
      // Transform form data to RouteRequest format
      const request: RouteRequest = {
        start: {
          latitude: 0, // Will be geocoded by the backend
          longitude: 0,
          name: formData.start
        },
        destination: {
          latitude: 0, // Will be geocoded by the backend
          longitude: 0,
          name: formData.destination
        },
        waypoints: formData.waypoints.map((waypoint: string) => ({
          latitude: 0, // Will be geocoded by the backend
          longitude: 0,
          name: waypoint
        })),
        vehicle_range: formData.vehicleRange
      };
      
      const response = await routeService.calculateRoute(request);
      return response;
    } catch (err: any) {
      setError(err.message || 'Failed to calculate route');
      return null;
    } finally {
      setLoading(false);
    }
  };
  
  return { calculateRoute, loading, error };
};
```

#### API Service

```tsx
// frontend/src/services/routeService.ts
import axios from 'axios';
import { RouteRequest, RouteResponse } from '../types/route';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class RouteService {
  async calculateRoute(request: RouteRequest): Promise<RouteResponse> {
    try {
      const response = await axios.post(`${API_URL}/routes/calculate`, request);
      return response.data;
    } catch (error: any) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to calculate route');
      }
      throw new Error('Network error occurred');
    }
  }
  
  async getChargingStations(latitude: number, longitude: number, radius: number = 10) {
    try {
      const response = await axios.get(`${API_URL}/charging-stations`, {
        params: { latitude, longitude, radius }
      });
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch charging stations');
    }
  }
}

export const routeService = new RouteService();
```

#### Type Definitions

```tsx
// frontend/src/types/route.ts
export interface Location {
  latitude: number;
  longitude: number;
  name?: string;
  address?: string;
}

export interface RouteRequest {
  start: Location;
  destination: Location;
  waypoints?: Location[];
  vehicle_range: number;
}

export interface RouteSegment {
  start_location: Location;
  end_location: Location;
  distance: number;
  duration: number;
  is_charging_stop: boolean;
  charging_time?: number;
  charge_to_level?: number;
  polyline?: string;
}

export interface ChargingStop {
  location: Location;
  charging_time: number;
  charge_to_level: number;
}

export interface RouteResponse {
  route_segments: RouteSegment[];
  total_distance: number;
  total_duration: number;
  charging_stops: ChargingStop[];
}
```

## Integration and Data Flow

### Docker Compose for Local Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  neo4j:
    image: neo4j:4.4
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/evrouter
      - NEO4J_dbms_memory_heap_max__size=2G
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - neo4j_import:/var/lib/neo4j/import
    networks:
      - evrouter-network

  backend:
    build: 
      context: ./backend
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=evrouter
    volumes:
      - ./backend:/app
    depends_on:
      - neo4j
    networks:
      - evrouter-network
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - REACT_APP_API_URL=http://localhost:8000/api/v1
    depends_on:
      - backend
    networks:
      - evrouter-network

volumes:
  neo4j_data:
  neo4j_logs:
  neo4j_import:

networks:
  evrouter-network:
    driver: bridge
```

## Development and Testing

### Local Development Setup

1. Clone the repository and navigate to the project directory:
```bash
git clone [repository-url]
cd EVrouter
```

2. Create backend and frontend directories:
```bash
mkdir -p backend/app/{api,core,db,models,services,utils}
mkdir -p frontend/src/{components,hooks,services,utils,contexts,types}
```

3. Start the Neo4j database:
```bash
docker-compose up -d neo4j
```

4. Install backend dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install fastapi uvicorn neo4j pydantic requests
```

5. Install frontend dependencies:
```bash
cd frontend
npm install
```

6. Start the backend development server:
```bash
cd backend
uvicorn main:app --reload
```

7. Start the frontend development server:
```bash
cd frontend
npm start
```

8. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs
   - Neo4j Browser: http://localhost:7474

### Testing

1. Backend Testing:
```bash
cd backend
pytest
```

2. Frontend Testing:
```bash
cd frontend
npm test
```

3. End-to-End Testing:
```bash
cd frontend
npm run cypress:open
```
