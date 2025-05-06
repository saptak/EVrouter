import axios from 'axios';
import { Location } from '../types/route';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class GeocodingService {
  async geocodeLocation(city: string): Promise<Location> {
    try {
      const response = await axios.get(`${API_URL}/v1/geocoding`, {
        params: { city }
      });
      return response.data;
    } catch (error: any) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to geocode location');
      }
      throw new Error('Network error occurred');
    }
  }
}

export const geocodingService = new GeocodingService(); 