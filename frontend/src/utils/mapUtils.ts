/**
 * Decodes a polyline string to a list of coordinates.
 * Based on the algorithm described at:
 * https://developers.google.com/maps/documentation/utilities/polylinealgorithm
 */
export const decodePolyline = (encoded: string): [number, number][] => {
  if (!encoded || encoded.startsWith('mock_polyline_')) {
    // For mock polylines, extract coordinates from the string
    if (encoded && encoded.startsWith('mock_polyline_')) {
      const parts = encoded.split('_');
      if (parts.length >= 5) {
        const startLat = parseFloat(parts[2]);
        const startLng = parseFloat(parts[3]);
        const endLat = parseFloat(parts[4]);
        const endLng = parseFloat(parts[5]);
        
        // Create a simple line between start and end
        return [
          [startLat, startLng],
          [startLat + (endLat - startLat) / 3, startLng + (endLng - startLng) / 3],
          [startLat + 2 * (endLat - startLat) / 3, startLng + 2 * (endLng - startLng) / 3],
          [endLat, endLng]
        ];
      }
    }
    
    // Return empty array for missing or invalid polyline
    return [];
  }
  
  const points: [number, number][] = [];
  let index = 0;
  const len = encoded.length;
  let lat = 0;
  let lng = 0;
  
  while (index < len) {
    let b;
    let shift = 0;
    let result = 0;
    
    do {
      b = encoded.charCodeAt(index++) - 63;
      result |= (b & 0x1f) << shift;
      shift += 5;
    } while (b >= 0x20);
    
    const dlat = ((result & 1) ? ~(result >> 1) : (result >> 1));
    lat += dlat;
    
    shift = 0;
    result = 0;
    
    do {
      b = encoded.charCodeAt(index++) - 63;
      result |= (b & 0x1f) << shift;
      shift += 5;
    } while (b >= 0x20);
    
    const dlng = ((result & 1) ? ~(result >> 1) : (result >> 1));
    lng += dlng;
    
    points.push([lat * 1e-5, lng * 1e-5]);
  }
  
  return points;
};

/**
 * Formats a duration in minutes to a human-readable string.
 */
export const formatDuration = (minutes: number): string => {
  const hours = Math.floor(minutes / 60);
  const mins = Math.round(minutes % 60);
  
  if (hours === 0) {
    return `${mins} min`;
  }
  
  return `${hours}h ${mins}m`;
};

/**
 * Formats a distance in kilometers to a human-readable string.
 */
export const formatDistance = (kilometers: number): string => {
  return `${kilometers.toFixed(1)} km`;
};
