import React, { useState } from 'react';

interface RouteFormProps {
  onSubmit: (formData: any) => void;
  isLoading: boolean;
}

const RouteForm: React.FC<RouteFormProps> = ({ onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    start: '',
    destination: '',
    waypoints: [] as string[],
    vehicleRange: 300,
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleRangeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    setFormData((prev) => ({
      ...prev,
      vehicleRange: value,
    }));
  };

  const handleAddWaypoint = () => {
    setFormData((prev) => ({
      ...prev,
      waypoints: [...prev.waypoints, ''],
    }));
  };

  const handleWaypointChange = (index: number, value: string) => {
    const updatedWaypoints = [...formData.waypoints];
    updatedWaypoints[index] = value;
    setFormData((prev) => ({
      ...prev,
      waypoints: updatedWaypoints,
    }));
  };

  const handleRemoveWaypoint = (index: number) => {
    const updatedWaypoints = formData.waypoints.filter((_, i) => i !== index);
    setFormData((prev) => ({
      ...prev,
      waypoints: updatedWaypoints,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-4 rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Plan Your EV Route</h2>
      
      <div className="mb-4">
        <label htmlFor="start" className="block text-sm font-medium mb-1">
          Start Location
        </label>
        <input
          id="start"
          name="start"
          value={formData.start}
          onChange={handleInputChange}
          placeholder="Enter start location"
          className="w-full p-2 border border-gray-300 rounded"
          required
        />
      </div>
      
      <div className="mb-4">
        <label htmlFor="destination" className="block text-sm font-medium mb-1">
          Destination
        </label>
        <input
          id="destination"
          name="destination"
          value={formData.destination}
          onChange={handleInputChange}
          placeholder="Enter destination"
          className="w-full p-2 border border-gray-300 rounded"
          required
        />
      </div>
      
      {formData.waypoints.map((waypoint, index) => (
        <div key={index} className="mb-4 flex items-center">
          <div className="flex-grow">
            <label className="block text-sm font-medium mb-1">
              Waypoint {index + 1}
            </label>
            <input
              value={waypoint}
              onChange={(e) => handleWaypointChange(index, e.target.value)}
              placeholder={`Enter waypoint ${index + 1}`}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
          <button
            type="button"
            onClick={() => handleRemoveWaypoint(index)}
            className="ml-2 mt-5 p-2 bg-red-500 text-white rounded hover:bg-red-600"
          >
            Remove
          </button>
        </div>
      ))}
      
      <button
        type="button"
        onClick={handleAddWaypoint}
        className="mb-4 p-2 bg-gray-200 rounded hover:bg-gray-300"
      >
        Add Waypoint
      </button>
      
      <div className="mb-6">
        <label htmlFor="vehicleRange" className="block text-sm font-medium mb-1">
          Vehicle Range: {formData.vehicleRange} km
        </label>
        <input
          id="vehicleRange"
          type="range"
          min={100}
          max={800}
          step={10}
          value={formData.vehicleRange}
          onChange={handleRangeChange}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-500">
          <span>100 km</span>
          <span>800 km</span>
        </div>
      </div>
      
      <button 
        type="submit" 
        disabled={isLoading} 
        className="w-full p-2 bg-primary text-white rounded hover:bg-primary-dark disabled:bg-gray-400"
      >
        {isLoading ? 'Calculating Route...' : 'Calculate Route'}
      </button>
    </form>
  );
};

export default RouteForm;
