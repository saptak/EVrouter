import { useState } from 'react';
import { RouteRequest, RouteResponse, Location } from '../types/route';
import { routeService } from '../services/routeService';

export const useRouteCalculation = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const calculateRoute = async (formData: any): Promise<RouteResponse | null> => {
    setLoading(true);
    setError(null);
    
    try {
      // For demo purposes, use mock coordinates
      // In a real app, we would geocode the addresses
      const mockStartCoords = { latitude: 40.7128, longitude: -74.0060 }; // New York
      const mockDestCoords = { latitude: 34.0522, longitude: -118.2437 }; // Los Angeles
      
      // Transform form data to RouteRequest format
      const request: RouteRequest = {
        start: {
          ...mockStartCoords,
          name: formData.start
        },
        destination: {
          ...mockDestCoords,
          name: formData.destination
        },
        waypoints: formData.waypoints.map((waypoint: string, index: number) => {
          // Generate some waypoint coordinates between start and destination
          const progress = (index + 1) / (formData.waypoints.length + 1);
          return {
            latitude: mockStartCoords.latitude + (mockDestCoords.latitude - mockStartCoords.latitude) * progress,
            longitude: mockStartCoords.longitude + (mockDestCoords.longitude - mockStartCoords.longitude) * progress,
            name: waypoint
          } as Location;
        }),
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
