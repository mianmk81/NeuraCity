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
      <label className="block text-sm font-medium text-gray-300 mb-2">
        GPS Location {required && <span className="text-red-400">*</span>}
      </label>

      {!location ? (
        <button
          type="button"
          onClick={captureLocation}
          disabled={loading}
          className={`w-full flex items-center justify-center px-4 py-4 glass border border-gray-500/30 rounded-lg text-base font-medium transition-all min-h-[48px] ${
            loading
              ? 'text-gray-500 cursor-not-allowed'
              : 'text-white hover:border-cyan-500/50 hover:bg-cyan-500/10 active:bg-cyan-500/20'
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
        <div className="glass border-2 border-green-500/30 rounded-lg p-4">
          <div className="flex items-start">
            <CheckCircle className="h-5 w-5 text-green-400 mr-3 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-medium text-green-400 mb-1">
                Location captured successfully
              </p>
              <div className="text-sm text-gray-300 space-y-1">
                <p>
                  <span className="font-medium text-cyan-400">Latitude:</span> {location.lat.toFixed(6)}
                </p>
                <p>
                  <span className="font-medium text-cyan-400">Longitude:</span> {location.lng.toFixed(6)}
                </p>
              </div>
              <button
                type="button"
                onClick={captureLocation}
                className="mt-2 text-xs text-green-400 hover:text-green-300 underline transition-colors"
              >
                Recapture location
              </button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-2 p-3 glass border border-red-500/30 rounded-lg">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}
    </div>
  );
};

export default GPSCapture;
