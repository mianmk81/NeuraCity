import { useState } from 'react';
import { MapPin, Loader2, CheckCircle } from 'lucide-react';

const GPSCapture = ({ onLocationCapture, required = false }) => {
  const [loading, setLoading] = useState(false);
  const [location, setLocation] = useState(null);
  const [error, setError] = useState(null);

  const captureLocation = () => {
    setLoading(true);
    setError(null);

    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser');
      setLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const coords = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        };
        setLocation(coords);
        setLoading(false);
        onLocationCapture(coords);
      },
      (err) => {
        let errorMsg = 'Failed to get location';
        switch (err.code) {
          case err.PERMISSION_DENIED:
            errorMsg = 'Location permission denied. Please allow location access.';
            break;
          case err.POSITION_UNAVAILABLE:
            errorMsg = 'Location information unavailable';
            break;
          case err.TIMEOUT:
            errorMsg = 'Location request timed out';
            break;
          default:
            errorMsg = 'An unknown error occurred';
        }
        setError(errorMsg);
        setLoading(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );
  };

  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        GPS Location {required && <span className="text-red-500">*</span>}
      </label>

      {!location ? (
        <button
          type="button"
          onClick={captureLocation}
          disabled={loading}
          className={`w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg text-sm font-medium transition-colors ${
            loading
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-white text-gray-700 hover:bg-gray-50'
          }`}
        >
          {loading ? (
            <>
              <Loader2 className="animate-spin h-5 w-5 mr-2" />
              Getting location...
            </>
          ) : (
            <>
              <MapPin className="h-5 w-5 mr-2" />
              Capture GPS Location
            </>
          )}
        </button>
      ) : (
        <div className="border-2 border-green-300 bg-green-50 rounded-lg p-4">
          <div className="flex items-start">
            <CheckCircle className="h-5 w-5 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-medium text-green-800 mb-1">
                Location captured successfully
              </p>
              <div className="text-sm text-green-700 space-y-1">
                <p>
                  <span className="font-medium">Latitude:</span> {location.lat.toFixed(6)}
                </p>
                <p>
                  <span className="font-medium">Longitude:</span> {location.lng.toFixed(6)}
                </p>
              </div>
              <button
                type="button"
                onClick={captureLocation}
                className="mt-2 text-xs text-green-600 hover:text-green-800 underline"
              >
                Recapture location
              </button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}
    </div>
  );
};

export default GPSCapture;
