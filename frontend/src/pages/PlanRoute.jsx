import { Loader2, MapPin, Navigation, Search, X } from 'lucide-react';
import { useEffect, useState, useRef } from 'react';
import Map2D from '../components/Map2D';
import RouteCard from '../components/RouteCard';
import { getNoiseData, getTrafficData, planRoute } from '../lib/api';

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
  const [originInput, setOriginInput] = useState('');
  const [destinationInput, setDestinationInput] = useState('');
  const [clickMode, setClickMode] = useState('origin'); // 'origin' or 'destination'
  const [noiseSegments, setNoiseSegments] = useState([]);
  const [trafficSegments, setTrafficSegments] = useState([]);
  const [heatmapLoading, setHeatmapLoading] = useState(false);
  
  // Use ref to track click state to avoid React state batching issues
  const clickStateRef = useRef({ origin: null, destination: null });

  // Fetch contextual heatmap data based on route type
  useEffect(() => {
    const fetchHeatmapData = async () => {
      setHeatmapLoading(true);
      try {
        if (routeType === 'quiet_walk') {
          // Show noise data for quiet walk
          const noise = await getNoiseData();
          setNoiseSegments(noise || []);
          setTrafficSegments([]);
        } else if (routeType === 'eco' || routeType === 'drive') {
          // Show traffic data for eco and regular drive
          const traffic = await getTrafficData();
          setTrafficSegments(traffic || []);
          setNoiseSegments([]);
        } else {
          setNoiseSegments([]);
          setTrafficSegments([]);
        }
      } catch (err) {
        console.error('Failed to fetch heatmap data:', err);
      } finally {
        setHeatmapLoading(false);
      }
    };

    fetchHeatmapData();
  }, [routeType]);

  const handleMapClick = (coords) => {
    // Use ref to check current state immediately (avoids React state batching issues)
    const currentOrigin = clickStateRef.current.origin;
    const currentDestination = clickStateRef.current.destination;
    
    // First click: Set origin (start pin) - only if origin is not set
    if (!currentOrigin) {
      clickStateRef.current.origin = coords;
      setOrigin(coords);
      setOriginInput(`${coords.lat.toFixed(6)}, ${coords.lng.toFixed(6)}`);
      setClickMode('destination'); // Switch to destination mode
      setRoute(null); // Clear existing route
      return; // Important: return early to prevent further execution
    }
    
    // Second click: Set destination (end pin) - only if destination is not set
    if (!currentDestination) {
      clickStateRef.current.destination = coords;
      setDestination(coords);
      setDestinationInput(`${coords.lat.toFixed(6)}, ${coords.lng.toFixed(6)}`);
      setRoute(null); // Clear existing route
      return; // Important: return early
    }
    
    // Both pins are set, clicking again resets and starts over
    clickStateRef.current.origin = coords;
    clickStateRef.current.destination = null;
    setOrigin(coords);
    setDestination(null);
    setOriginInput(`${coords.lat.toFixed(6)}, ${coords.lng.toFixed(6)}`);
    setDestinationInput('');
    setClickMode('destination');
    setRoute(null);
  };

  const geocodeAddress = async (address) => {
    try {
        const response = await fetch(
          `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}, New York, NY&limit=1`
        );
      const data = await response.json();
      if (data && data.length > 0) {
        return {
          lat: parseFloat(data[0].lat),
          lng: parseFloat(data[0].lon)
        };
      }
      return null;
    } catch (error) {
      console.error('Geocoding error:', error);
      return null;
    }
  };

  const handleOriginInputChange = (e) => {
    const value = e.target.value;
    setOriginInput(value);
  };

  const handleDestinationInputChange = (e) => {
    const value = e.target.value;
    setDestinationInput(value);
  };

  const handleSearchOrigin = async () => {
    if (!originInput.trim()) return;
    
    setLoading(true);
    setError(null);
    
    // Try to parse as coordinates first
    const parts = originInput.split(',').map(p => p.trim());
    if (parts.length === 2) {
      const lat = parseFloat(parts[0]);
      const lng = parseFloat(parts[1]);
      if (!isNaN(lat) && !isNaN(lng) && lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
        const coords = { lat, lng };
        clickStateRef.current.origin = coords;
        setOrigin(coords);
        setRoute(null);
        setLoading(false);
        return;
      }
    }
    
    // Otherwise, geocode as address
    const result = await geocodeAddress(originInput);
    if (result) {
      clickStateRef.current.origin = result;
      setOrigin(result);
      setOriginInput(`${result.lat.toFixed(6)}, ${result.lng.toFixed(6)}`);
      setClickMode('destination');
      setRoute(null);
    } else {
      setError(`Could not find location: "${originInput}". Try "Broadway" or coordinates.`);
    }
    setLoading(false);
  };

  const handleSearchDestination = async () => {
    if (!destinationInput.trim()) return;
    
    setLoading(true);
    setError(null);
    
    // Try to parse as coordinates first
    const parts = destinationInput.split(',').map(p => p.trim());
    if (parts.length === 2) {
      const lat = parseFloat(parts[0]);
      const lng = parseFloat(parts[1]);
      if (!isNaN(lat) && !isNaN(lng) && lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
        const coords = { lat, lng };
        clickStateRef.current.destination = coords;
        setDestination(coords);
        setRoute(null);
        setLoading(false);
        return;
      }
    }
    
    // Otherwise, geocode as address
    const result = await geocodeAddress(destinationInput);
    if (result) {
      clickStateRef.current.destination = result;
      setDestination(result);
      setDestinationInput(`${result.lat.toFixed(6)}, ${result.lng.toFixed(6)}`);
      setRoute(null);
    } else {
      setError(`Could not find location: "${destinationInput}". Try "Times Square" or coordinates.`);
    }
    setLoading(false);
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
    clickStateRef.current.origin = null;
    clickStateRef.current.destination = null;
    setOrigin(null);
    setDestination(null);
    setRoute(null);
    setError(null);
    setOriginInput('');
    setDestinationInput('');
    setClickMode('origin'); // Reset to origin mode for first click
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
                  <span>Click on the map to place your <strong className="text-green-600">start pin</strong> (green)</span>
                </li>
                <li className="flex items-start">
                  <span className="font-medium text-primary-600 mr-2">2.</span>
                  <span>Click again to place your <strong className="text-red-600">destination pin</strong> (red)</span>
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
              
              <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-xs text-blue-800">
                  <strong>3 Ways to Select:</strong>
                  <br />1. Click map
                  <br />2. Type address: "Broadway", "Times Square"
                  <br />3. Type coordinates: 40.7128, -74.0060
                </p>
              </div>

              <div className="space-y-4">
                {/* Origin */}
                <div>
                  <label className="text-sm font-medium text-gray-700 flex items-center mb-2">
                    <MapPin className="h-4 w-4 mr-1 text-green-600" />
                    Origin {clickMode === 'origin' && <span className="ml-2 text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">Click map here</span>}
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={originInput}
                      onChange={handleOriginInputChange}
                      onKeyPress={(e) => e.key === 'Enter' && handleSearchOrigin()}
                      placeholder="Type address or coordinates..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    />
                    <button
                      onClick={handleSearchOrigin}
                      disabled={!originInput.trim() || loading}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center"
                    >
                      <Search className="h-4 w-4" />
                    </button>
                  </div>
                  {origin && (
                    <div className="mt-2 p-2 bg-green-50 rounded border border-green-200">
                      <p className="text-xs text-green-800">
                        ✓ Set: {origin.lat.toFixed(6)}, {origin.lng.toFixed(6)}
                      </p>
                    </div>
                  )}
                </div>

                {/* Destination */}
                <div>
                  <label className="text-sm font-medium text-gray-700 flex items-center mb-2">
                    <MapPin className="h-4 w-4 mr-1 text-red-600" />
                    Destination {clickMode === 'destination' && <span className="ml-2 text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded">Click map here</span>}
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={destinationInput}
                      onChange={handleDestinationInputChange}
                      onKeyPress={(e) => e.key === 'Enter' && handleSearchDestination()}
                      placeholder="Type address or coordinates..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    />
                    <button
                      onClick={handleSearchDestination}
                      disabled={!destinationInput.trim() || loading}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center"
                    >
                      <Search className="h-4 w-4" />
                    </button>
                  </div>
                  {destination && (
                    <div className="mt-2 p-2 bg-red-50 rounded border border-red-200">
                      <p className="text-xs text-red-800">
                        ✓ Set: {destination.lat.toFixed(6)}, {destination.lng.toFixed(6)}
                      </p>
                    </div>
                  )}
                </div>
                
                {/* Status indicator */}
                {!origin && !destination && (
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-xs text-blue-800">
                      <strong>Ready:</strong> Click the map to place your first pin (start point)
                    </p>
                  </div>
                )}
                {origin && !destination && (
                  <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-xs text-yellow-800">
                      <strong>Start set:</strong> Click the map again to place your destination pin
                    </p>
                  </div>
                )}
                {origin && destination && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-xs text-green-800">
                      <strong>Both pins set:</strong> Click "Plan Route" or click the map again to reset
                    </p>
                  </div>
                )}
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
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{type.label}</p>
                      <p className="text-xs text-gray-600">{type.description}</p>
                      {routeType === type.value && (
                        <div className="mt-2 text-xs text-primary-700 font-medium">
                          {type.value === 'quiet_walk' && '🔊 Showing noise heatmap'}
                          {(type.value === 'eco' || type.value === 'drive') && '🚗 Showing traffic heatmap'}
                        </div>
                      )}
                    </div>
                  </label>
                ))}
              </div>
              
              {heatmapLoading && (
                <div className="mt-3 flex items-center text-xs text-gray-500">
                  <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                  Loading heatmap data...
                </div>
              )}
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
                noiseSegments={noiseSegments}
                trafficSegments={trafficSegments}
                center={[40.7128, -74.0060]} // New York City
                zoom={13}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlanRoute;
