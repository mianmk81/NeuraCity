import { Clock, MapPin, Leaf, Volume2 } from 'lucide-react';
import { formatDistance, formatDuration } from '../lib/helpers.js';

const RouteCard = ({ route }) => {
  if (!route) return null;

  const { route_type, metrics, explanation } = route;
  const { distance_km, eta_minutes, co2_kg, avg_noise_db } = metrics || {};

  return (
    <div className="glass rounded-lg shadow-lg p-6 border border-blue-500/30">
      <h3 className="text-lg font-semibold text-white mb-4 neon-blue">
        Route Details
      </h3>

      <div className="space-y-4">
        {/* ETA and Distance */}
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center">
            <Clock className="h-5 w-5 text-cyan-400 mr-2" />
            <div>
              <p className="text-xs text-gray-400">Estimated Time</p>
              <p className="text-sm font-medium text-white">
                {formatDuration(eta_minutes)}
              </p>
            </div>
          </div>
          <div className="flex items-center">
            <MapPin className="h-5 w-5 text-cyan-400 mr-2" />
            <div>
              <p className="text-xs text-gray-400">Distance</p>
              <p className="text-sm font-medium text-white">
                {formatDistance(distance_km)}
              </p>
            </div>
          </div>
        </div>

        {/* Route Type Specific Metrics */}
        {route_type === 'eco' && co2_kg !== undefined && (
          <div className="flex items-center p-3 glass border border-green-500/30 rounded-lg">
            <Leaf className="h-5 w-5 text-green-400 mr-2" />
            <div>
              <p className="text-xs text-green-400 font-medium">CO₂ Emissions</p>
              <p className="text-sm text-gray-300">
                {co2_kg.toFixed(2)} kg - Low emissions route
              </p>
            </div>
          </div>
        )}

        {route_type === 'quiet_walk' && avg_noise_db !== undefined && (
          <div className="flex items-center p-3 glass border border-blue-500/30 rounded-lg">
            <Volume2 className="h-5 w-5 text-blue-400 mr-2" />
            <div>
              <p className="text-xs text-blue-400 font-medium">Average Noise</p>
              <p className="text-sm text-gray-300">
                {avg_noise_db.toFixed(1)} dB - Quiet route
              </p>
            </div>
          </div>
        )}

        {/* AI Explanation */}
        {explanation && (
          <div className="border-t border-blue-500/30 pt-4">
            <p className="text-xs text-gray-400 mb-2">Route Analysis</p>
            <p className="text-sm text-gray-300 leading-relaxed">
              {explanation}
            </p>
          </div>
        )}

        {/* Route Type Badge */}
        <div className="flex items-center justify-between pt-2 border-t border-blue-500/30">
          <span className="text-xs text-gray-400">Route Type</span>
          <span className={`px-3 py-1 rounded-full text-xs font-medium border ${
            route_type === 'drive' ? 'bg-blue-500/20 text-blue-400 border-blue-500/50' :
            route_type === 'eco' ? 'bg-green-500/20 text-green-400 border-green-500/50' :
            'bg-purple-500/20 text-purple-400 border-purple-500/50'
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
