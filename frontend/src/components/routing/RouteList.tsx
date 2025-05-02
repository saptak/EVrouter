import React from 'react';
import { RouteResponse, RouteSegment } from '../../types/route';
import { formatDuration, formatDistance } from '../../utils/mapUtils';

interface RouteListProps {
  route: RouteResponse;
}

const RouteList: React.FC<RouteListProps> = ({ route }) => {
  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Route Details</h2>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <span className="text-sm text-gray-500">Total Distance</span>
          <p className="text-lg font-medium">{formatDistance(route.total_distance)}</p>
        </div>
        <div>
          <span className="text-sm text-gray-500">Total Duration</span>
          <p className="text-lg font-medium">
            {formatDuration(route.total_duration)}
          </p>
        </div>
        <div>
          <span className="text-sm text-gray-500">Charging Stops</span>
          <p className="text-lg font-medium">{route.charging_stops.length}</p>
        </div>
        <div>
          <span className="text-sm text-gray-500">Total Charging Time</span>
          <p className="text-lg font-medium">
            {formatDuration(route.charging_stops.reduce((sum, stop) => sum + stop.charging_time, 0))}
          </p>
        </div>
      </div>
      
      <div className="border-t pt-4">
        <h3 className="text-lg font-medium mb-2">Route Segments</h3>
        
        <div className="space-y-4">
          {route.route_segments.map((segment, index) => (
            <RouteSegmentItem key={index} segment={segment} index={index} />
          ))}
        </div>
      </div>
    </div>
  );
};

interface RouteSegmentItemProps {
  segment: RouteSegment;
  index: number;
}

const RouteSegmentItem: React.FC<RouteSegmentItemProps> = ({ segment, index }) => {
  return (
    <div className={`p-3 rounded ${segment.is_charging_stop ? 'bg-green-50' : 'bg-gray-50'}`}>
      <div className="flex items-center mb-2">
        <div className="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center mr-2">
          {index + 1}
        </div>
        <div>
          <h4 className="font-medium">
            {segment.start_location.name || 'Unknown'} → {segment.end_location.name || 'Unknown'}
          </h4>
        </div>
      </div>
      
      <div className="ml-10">
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <span className="text-gray-500">Distance:</span> {formatDistance(segment.distance)}
          </div>
          <div>
            <span className="text-gray-500">Duration:</span> {formatDuration(segment.duration)}
          </div>
        </div>
        
        {segment.is_charging_stop && segment.charging_time && segment.charge_to_level && (
          <div className="mt-2 p-2 bg-green-100 rounded text-sm">
            <div className="font-medium text-green-800 mb-1">Charging Stop</div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="text-gray-600">Charging Time:</span> {formatDuration(segment.charging_time)}
              </div>
              <div>
                <span className="text-gray-600">Charge to:</span> {segment.charge_to_level.toFixed(0)}%
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RouteList;
