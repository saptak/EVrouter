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
