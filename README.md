# EVrouter: Electric Vehicle Routing Application
## Product Requirements Document

## 1. Overview

EVrouter is a web application designed to help electric vehicle (EV) drivers plan optimal routes that include necessary charging stops. The application takes into account the vehicle's range and plots a journey with strategically placed charging stations, indicating how much charging is needed at each stop to complete the journey efficiently.

## 2. Problem Statement

EV drivers face "range anxiety" when planning longer trips, requiring careful planning to ensure they don't run out of charge. Existing mapping solutions don't adequately address:
- When and where to stop for charging
- How much to charge at each stop (to minimize overall travel time)
- Integration of real-time charging station availability
- Route optimization based on EV-specific parameters

EVrouter solves these problems by providing a specialized routing solution for EV drivers.

## 3. User Personas

### Primary: EV Owner (Daily Commuter)
- Uses their EV for daily transportation
- Occasionally makes longer trips that exceed vehicle range
- Values time efficiency and minimal stops

### Secondary: EV Road Tripper
- Plans longer journeys in their EV
- Needs to carefully plan multiple charging stops
- Wants to optimize charging time vs. driving time

### Tertiary: New EV Owner
- Recently purchased their first EV
- Experiencing range anxiety
- Needs guidance on charging infrastructure

## 4. Features and Requirements

### 4.1 Core Features

#### Route Planning
- Input start point, destination, and waypoints
- Input vehicle range
- Display optimized route with charging stops
- Show charging time requirements at each stop
- Display total journey time (driving + charging)

#### Charging Station Integration
- Display comprehensive charging station information
- Filter stations by connector type
- Show real-time availability (future enhancement)
- Display charging speed capabilities

#### Map Visualization
- Interactive map showing complete route
- Charging stations clearly marked
- Range circles to indicate vehicle limits
- Turn-by-turn directions

#### Route List View
- Detailed breakdown of journey segments
- Charging station details at each stop
- Estimated charging time at each stop
- Total journey statistics

### 4.2 Technical Requirements

#### Backend
- Neo4j graph database for route data and charging network
- Python-based API for route calculation
- Integration with mapping services (OpenStreetMap or similar)
- Charging station database

#### Frontend
- React-based single-page application
- shadcn/ui component library for UI elements
- Responsive design for mobile and desktop use
- Interactive map component

## 5. Technical Architecture

### 5.1 System Components

#### Database Layer (Neo4j)
- Road network as a graph database
- Charging station nodes with metadata
- Efficient pathfinding capabilities

#### Application Layer (Python)
- Django or FastAPI for backend API
- Route calculation algorithms
- Integration with mapping services
- Authentication and user management

#### Presentation Layer (React)
- React frontend with shadcn/ui components
- Map visualization (Leaflet or Google Maps)
- User interface for inputs and outputs
- Responsive design

### 5.2 Data Flow

1. User inputs route parameters (start, end, waypoints, vehicle range)
2. Frontend sends request to Python backend
3. Backend queries Neo4j for optimal route considering:
   - Road network
   - Vehicle range constraints
   - Available charging stations
   - Optimal charging strategy
4. Backend returns calculated route with charging stops
5. Frontend displays route on map and in list format

## 6. User Interface Design

### 6.1 Main Screen

- Sidebar for input parameters
  - Start location (text input with autocomplete)
  - Destination (text input with autocomplete)
  - Waypoints (optional, multiple inputs)
  - Vehicle range (slider or numeric input)
  - Vehicle model (optional dropdown for presets)

- Main content area
  - Map view taking majority of screen
  - Toggle between map-only and split view

- Results panel
  - Summary statistics (total distance, time, charging stops)
  - Expandable list of route segments
  - Charging information for each stop

### 6.2 Map View

- Interactive map showing complete route
- Color-coded route segments based on range
- Charging station markers
- Click-to-expand information panels
- Range visualization (optional overlay)

### 6.3 List View

- Chronological breakdown of route
- Driving segments with distance and estimated time
- Charging stops with:
  - Location name and address
  - Required charging time
  - Charge percentage needed
  - Amenities available (future feature)

## 7. Implementation Details

### 7.1 Backend

#### Neo4j Database Setup
- Road network imported from OpenStreetMap
- Charging station data from open APIs (OpenChargeMap, etc.)
- Graph structure optimized for routing algorithms

#### Python API Implementation
- Django/FastAPI framework
- Routing algorithms utilizing Neo4j's graph capabilities
- REST API endpoints for:
  - Route calculation
  - Charging station queries
  - User preferences (future feature)

### 7.2 Frontend

#### React Application Structure
- Component-based architecture
- shadcn/ui for UI components
- State management with React hooks or Redux
- Map integration with Leaflet or similar library

#### Key Components
- RouteForm: Inputs for route parameters
- MapView: Interactive map display
- RouteList: Detailed journey breakdown
- ChargingStationInfo: Details for each charging stop

## 8. Local Development and Testing

### 8.1 Development Environment Setup

#### Prerequisites
- Docker and Docker Compose
- Node.js (v14 or higher)
- Python (v3.8 or higher)
- Git

#### Installation Steps
1. Clone repository: `git clone [repository-url]`
2. Set up Neo4j database:
   ```
   cd EVrouter
   docker-compose up -d neo4j
   ```
3. Set up Python backend:
   ```
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```
4. Set up React frontend:
   ```
   cd frontend
   npm install
   npm start
   ```

### 8.2 Testing

#### Backend Testing
- Unit tests for routing algorithms
- API tests for endpoint functionality
- Integration tests for Neo4j queries

#### Frontend Testing
- Component tests with React Testing Library
- End-to-end tests with Cypress
- Responsive design tests across devices

## 9. Future Enhancements

### Phase 2 Features
- User accounts and saved routes
- Real-time charging station availability
- Vehicle-specific profiles and battery degradation models
- Weather and elevation effects on range
- Integration with vehicle APIs for direct range data

### Phase 3 Features
- Mobile app versions
- Trip planning with accommodation suggestions
- Smart charging recommendations based on electricity pricing
- Integration with in-car navigation systems

## 10. Conclusion

The EVrouter application addresses a critical need for EV drivers by providing specialized route planning that accounts for charging requirements. By leveraging Neo4j's graph database capabilities and modern web technologies, the application will deliver an intuitive and efficient solution for overcoming range anxiety and optimizing EV journeys.
