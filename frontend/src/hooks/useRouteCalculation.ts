import { useState } from 'react';
import { RouteRequest, RouteResponse, Location } from '../types/route';
import { routeService } from '../services/routeService';
import { geocodingService } from '../services/geocodingService';

export const useRouteCalculation = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const calculateRoute = async (formData: any): Promise<RouteResponse | null> => {
    setLoading(true);
    setError(null);
    
    try {
      // Geocode the start and destination addresses
      const [startLocation, destLocation] = await Promise.all([
        geocodingService.geocodeLocation(formData.start),
        geocodingService.geocodeLocation(formData.destination)
      ]);
      
      // Transform form data to RouteRequest format
      const request: RouteRequest = {
        start: {
          ...startLocation,
          name: formData.start
        },
        destination: {
          ...destLocation,
          name: formData.destination
        },
        waypoints: await Promise.all(
          formData.waypoints.map(async (waypoint: string) => {
            const location = await geocodingService.geocodeLocation(waypoint);
            return {
              ...location,
              name: waypoint
            } as Location;
          })
        ),
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
