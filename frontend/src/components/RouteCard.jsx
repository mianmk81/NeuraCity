import { Clock, MapPin, Leaf, Volume2 } from 'lucide-react';
import { formatDistance, formatDuration } from '../lib/helpers';

const RouteCard = ({ route }) => {
  if (!route) return null;

  const { distance, eta, route_type, co2_score, noise_score, explanation } = route;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        Route Details
      </h3>

      <div className="space-y-4">
        {/* ETA and Distance */}
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center">
            <Clock className="h-5 w-5 text-primary-600 mr-2" />
            <div>
              <p className="text-xs text-gray-500">Estimated Time</p>
              <p className="text-sm font-medium text-gray-800">
                {formatDuration(eta)}
              </p>
            </div>
          </div>
          <div className="flex items-center">
            <MapPin className="h-5 w-5 text-primary-600 mr-2" />
            <div>
              <p className="text-xs text-gray-500">Distance</p>
              <p className="text-sm font-medium text-gray-800">
                {formatDistance(distance)}
              </p>
            </div>
          </div>
        </div>

        {/* Route Type Specific Metrics */}
        {route_type === 'eco' && co2_score !== undefined && (
          <div className="flex items-center p-3 bg-green-50 rounded-lg">
            <Leaf className="h-5 w-5 text-green-600 mr-2" />
            <div>
              <p className="text-xs text-green-600 font-medium">CO₂ Score</p>
              <p className="text-sm text-green-800">
                {co2_score.toFixed(2)} - Low emissions route
              </p>
            </div>
          </div>
        )}

        {route_type === 'quiet_walk' && noise_score !== undefined && (
          <div className="flex items-center p-3 bg-blue-50 rounded-lg">
            <Volume2 className="h-5 w-5 text-blue-600 mr-2" />
            <div>
              <p className="text-xs text-blue-600 font-medium">Average Noise</p>
              <p className="text-sm text-blue-800">
                {noise_score.toFixed(1)} dB - Quiet route
              </p>
            </div>
          </div>
        )}

        {/* AI Explanation */}
        {explanation && (
          <div className="border-t pt-4">
            <p className="text-xs text-gray-500 mb-2">Route Analysis</p>
            <p className="text-sm text-gray-700 leading-relaxed">
              {explanation}
            </p>
          </div>
        )}

        {/* Route Type Badge */}
        <div className="flex items-center justify-between pt-2 border-t">
          <span className="text-xs text-gray-500">Route Type</span>
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
            route_type === 'drive' ? 'bg-blue-100 text-blue-700' :
            route_type === 'eco' ? 'bg-green-100 text-green-700' :
            'bg-purple-100 text-purple-700'
          }`}>
            {route_type === 'drive' ? 'Driving' :
             route_type === 'eco' ? 'Eco Drive' :
             'Quiet Walk'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default RouteCard;
