"""Polyline encoding and decoding utilities"""

def encode_coordinates(coordinates):
    """
    Encode a sequence of coordinates as a polyline string.
    
    Args:
        coordinates: List of (lat, lng) coordinate pairs
        
    Returns:
        Encoded polyline string
    """
    result = []
    
    prev_lat = 0
    prev_lng = 0
    
    for lat, lng in coordinates:
        # Round to 5 decimal places and convert to integers
        lat_int = int(round(lat * 1e5))
        lng_int = int(round(lng * 1e5))
        
        # Compute delta from previous point
        d_lat = lat_int - prev_lat
        d_lng = lng_int - prev_lng
        
        # Update previous coordinates
        prev_lat = lat_int
        prev_lng = lng_int
        
        # Encode delta values
        result.append(_encode_value(d_lat))
        result.append(_encode_value(d_lng))
    
    return ''.join(result)

def decode_polyline(polyline):
    """
    Decode a polyline string to a list of (lat, lng) coordinate pairs.
    
    Args:
        polyline: Encoded polyline string
        
    Returns:
        List of (lat, lng) coordinate pairs
    """
    coordinates = []
    i = 0
    lat = 0
    lng = 0
    
    while i < len(polyline):
        # Decode latitude change
        d_lat, i = _decode_value(polyline, i)
        lat += d_lat
        
        # Decode longitude change
        d_lng, i = _decode_value(polyline, i)
        lng += d_lng
        
        # Convert back to float and add to result
        coordinates.append((lat / 1e5, lng / 1e5))
    
    return coordinates

def _encode_value(value):
    """Encode a single value according to the polyline algorithm"""
    # Invert negative values
    value = ~(value << 1) if value < 0 else (value << 1)
    
    # Convert to ASCII
    result = ''
    while value >= 0x20:
        result += chr((0x20 | (value & 0x1f)) + 63)
        value >>= 5
    result += chr(value + 63)
    
    return result

def _decode_value(polyline, index):
    """Decode a single value from a polyline string starting at index"""
    result = 0
    shift = 0
    
    while True:
        b = ord(polyline[index]) - 63
        index += 1
        result |= (b & 0x1f) << shift
        shift += 5
        if b < 0x20:
            break
    
    # Handle negative values
    result = ~(result >> 1) if result & 1 else (result >> 1)
    
    return result, index
