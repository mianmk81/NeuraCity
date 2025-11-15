import { useState } from 'react';
import Map2D from '../components/Map2D';
import RouteCard from '../components/RouteCard';
import { planRoute } from '../lib/api';
import { MapPin, Navigation, Loader2, X } from 'lucide-react';

const ROUTE_TYPES = [
  { value: 'drive', label: 'Drive', description: 'Fastest route avoiding accidents' },
  { value: 'eco', label: 'Eco Drive', description: 'Low emissions, minimal congestion' },
  { value: 'quiet_walk', label: 'Quiet Walk', description: 'Peaceful walking route' },
];

const PlanRoute = () => {
  const [origin, setOrigin] = useState(null);
  const [destination, setDestination] = useState(null);
  const [routeType, setRouteType] = useState('drive');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [route, setRoute] = useState(null);

  const handleMapClick = (coords) => {
    if (!origin) {
      setOrigin(coords);
    } else if (!destination) {
      setDestination(coords);
    } else {
      // Reset and start over
      setOrigin(coords);
      setDestination(null);
      setRoute(null);
    }
  };

  const handlePlanRoute = async () => {
    if (!origin || !destination) {
      setError('Please select both origin and destination on the map');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await planRoute(origin, destination, routeType);
      setRoute(result);
    } catch (err) {
      setError(err.message || 'Failed to plan route. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setOrigin(null);
    setDestination(null);
    setRoute(null);
    setError(null);
  };

  const markers = [];
  if (origin) {
    markers.push({ lat: origin.lat, lng: origin.lng, label: 'Start', color: '#10b981' });
  }
  if (destination) {
    markers.push({ lat: destination.lat, lng: destination.lng, label: 'End', color: '#ef4444' });
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Plan Your Route
          </h1>
          <p className="text-gray-600">
            Select origin and destination on the map, then choose your route type
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Panel - Controls */}
          <div className="lg:col-span-1 space-y-6">
            {/* Instructions */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Instructions</h3>
              <ol className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start">
                  <span className="font-medium text-primary-600 mr-2">1.</span>
                  Click on the map to set your starting point
                </li>
                <li className="flex items-start">
                  <span className="font-medium text-primary-600 mr-2">2.</span>
                  Click again to set your destination
                </li>
                <li className="flex items-start">
                  <span className="font-medium text-primary-600 mr-2">3.</span>
                  Choose your preferred route type
                </li>
                <li className="flex items-start">
                  <span className="font-medium text-primary-600 mr-2">4.</span>
                  Click "Plan Route" to see your optimal path
                </li>
              </ol>
            </div>

            {/* Location Selection */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Selected Points</h3>

              <div className="space-y-4">
                {/* Origin */}
                <div>
                  <label className="text-sm font-medium text-gray-700 flex items-center mb-2">
                    <MapPin className="h-4 w-4 mr-1 text-green-600" />
                    Origin
                  </label>
                  {origin ? (
                    <div className="p-3 bg-green-50 rounded border border-green-200">
                      <p className="text-xs text-green-800">
                        {origin.lat.toFixed(6)}, {origin.lng.toFixed(6)}
                      </p>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-400 italic">Click map to select</p>
                  )}
                </div>

                {/* Destination */}
                <div>
                  <label className="text-sm font-medium text-gray-700 flex items-center mb-2">
                    <MapPin className="h-4 w-4 mr-1 text-red-600" />
                    Destination
                  </label>
                  {destination ? (
                    <div className="p-3 bg-red-50 rounded border border-red-200">
                      <p className="text-xs text-red-800">
                        {destination.lat.toFixed(6)}, {destination.lng.toFixed(6)}
                      </p>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-400 italic">Click map to select</p>
                  )}
                </div>
              </div>

              {(origin || destination) && (
                <button
                  onClick={handleReset}
                  className="mt-4 w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  <X className="h-4 w-4 mr-2" />
                  Reset Points
                </button>
              )}
            </div>

            {/* Route Type Selection */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Route Type</h3>

              <div className="space-y-3">
                {ROUTE_TYPES.map((type) => (
                  <label
                    key={type.value}
                    className={`flex items-start p-3 border rounded-lg cursor-pointer transition-colors ${
                      routeType === type.value
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="routeType"
                      value={type.value}
                      checked={routeType === type.value}
                      onChange={(e) => setRouteType(e.target.value)}
                      className="mt-1 mr-3"
                    />
                    <div>
                      <p className="font-medium text-gray-900">{type.label}</p>
                      <p className="text-xs text-gray-600">{type.description}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Plan Button */}
            <button
              onClick={handlePlanRoute}
              disabled={!origin || !destination || loading}
              className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                origin && destination && !loading
                  ? 'bg-primary-600 text-white hover:bg-primary-700'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <Loader2 className="animate-spin h-5 w-5 mr-2" />
                  Planning Route...
                </span>
              ) : (
                <span className="flex items-center justify-center">
                  <Navigation className="h-5 w-5 mr-2" />
                  Plan Route
                </span>
              )}
            </button>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {/* Route Details */}
            {route && <RouteCard route={route} />}
          </div>

          {/* Right Panel - Map */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-4">
              <Map2D
                height="calc(100vh - 200px)"
                onMapClick={handleMapClick}
                markers={markers}
                route={route}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlanRoute;
