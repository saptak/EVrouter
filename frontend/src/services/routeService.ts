import axios from 'axios';
import { RouteRequest, RouteResponse } from '../types/route';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class RouteService {
  async calculateRoute(request: RouteRequest): Promise<RouteResponse> {
    try {
      const response = await axios.post(`${API_URL}/v1/routes/calculate`, request);
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
      const response = await axios.get(`${API_URL}/v1/charging-stations`, {
        params: { latitude, longitude, radius }
      });
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch charging stations');
    }
  }
}

export const routeService = new RouteService();
