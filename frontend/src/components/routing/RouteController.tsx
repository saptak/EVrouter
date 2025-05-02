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
        <div className="h-[500px] mb-4 bg-white rounded shadow">
          <MapView route={route} />
        </div>
        {route && <RouteList route={route} />}
      </div>
    </div>
  );
};

export default RouteController;
