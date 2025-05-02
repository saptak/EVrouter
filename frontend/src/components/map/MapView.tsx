import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { RouteResponse } from '../../types/route';
import { decodePolyline } from '../../utils/mapUtils';
import L from 'leaflet';

// Fix the marker icon issue in Leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

// Custom charging station icon
const chargingIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});

interface MapViewProps {
  route: RouteResponse | null;
}

const MapView: React.FC<MapViewProps> = ({ route }) => {
  const defaultCenter: [number, number] = [40.7128, -74.0060]; // New York City
  const defaultZoom = 5;
  
  return (
    <MapContainer 
      center={defaultCenter} 
      zoom={defaultZoom} 
      style={{ height: '100%', width: '100%' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      
      {route && <RouteLayer route={route} />}
    </MapContainer>
  );
};

interface RouteLayerProps {
  route: RouteResponse;
}

const RouteLayer: React.FC<RouteLayerProps> = ({ route }) => {
  const map = useMap();
  
  useEffect(() => {
    if (route && route.route_segments.length > 0) {
      // Get all coordinates for bounds
      const bounds: L.LatLngBounds = new L.LatLngBounds([]);
      
      route.route_segments.forEach(segment => {
        // Add start and end locations to bounds
        bounds.extend([segment.start_location.latitude, segment.start_location.longitude]);
        bounds.extend([segment.end_location.latitude, segment.end_location.longitude]);
        
        // Add decoded polyline points to bounds if available
        if (segment.polyline) {
          const points = decodePolyline(segment.polyline);
          points.forEach(point => bounds.extend([point[0], point[1]]));
        }
      });
      
      // Fit map to bounds with padding
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [route, map]);
  
  if (!route || route.route_segments.length === 0) {
    return null;
  }
  
  return (
    <>
      {route.route_segments.map((segment, index) => {
        // Decode polyline for the segment
        const positions = segment.polyline 
          ? decodePolyline(segment.polyline)
          : [
              [segment.start_location.latitude, segment.start_location.longitude],
              [segment.end_location.latitude, segment.end_location.longitude]
            ];
        
        return (
          <React.Fragment key={index}>
            {/* Start location marker - only for first segment */}
            {index === 0 && (
              <Marker position={[segment.start_location.latitude, segment.start_location.longitude]}>
                <Popup>
                  <strong>Start:</strong> {segment.start_location.name || 'Starting Point'}
                </Popup>
              </Marker>
            )}
            
            {/* End location marker */}
            <Marker 
              position={[segment.end_location.latitude, segment.end_location.longitude]}
              icon={segment.is_charging_stop ? chargingIcon : DefaultIcon}
            >
              <Popup>
                {segment.is_charging_stop ? (
                  <div>
                    <strong>Charging Stop:</strong> {segment.end_location.name || 'Charging Station'}<br />
                    {segment.charging_time && <><strong>Charging Time:</strong> {Math.round(segment.charging_time)} minutes<br /></>}
                    {segment.charge_to_level && <><strong>Charge to:</strong> {Math.round(segment.charge_to_level)}%</>}
                  </div>
                ) : (
                  <strong>{segment.end_location.name || 'Waypoint'}</strong>
                )}
              </Popup>
            </Marker>
            
            {/* Route line */}
            {positions.length > 0 && (
              <Polyline 
                positions={positions as [number, number][]}
                color={segment.is_charging_stop ? 'green' : 'blue'}
                weight={4}
              />
            )}
          </React.Fragment>
        );
      })}
    </>
  );
};

export default MapView;
