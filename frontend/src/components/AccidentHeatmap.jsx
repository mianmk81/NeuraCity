import { useState, useEffect, useMemo, memo } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, LayerGroup } from 'react-leaflet';
import { getAccidentHistory } from '../lib/api.js';
import { Flame, Calendar, Filter } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';
import 'leaflet/dist/leaflet.css';

const AccidentHeatmap = memo(({ showControls = true }) => {
  const [accidents, setAccidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState('all');
  const [severityFilter, setSeverityFilter] = useState('all');

  useEffect(() => {
    fetchAccidentData();
  }, [dateRange, severityFilter]);

  const fetchAccidentData = async () => {
    setLoading(true);
    try {
      // Mock accident data - backend will implement later
      const mockAccidents = [
        { id: 1, lat: 37.7849, lng: -122.4094, severity: 0.85, count: 5, date: '2025-01-10' },
        { id: 2, lat: 37.7749, lng: -122.4194, severity: 0.92, count: 8, date: '2025-01-12' },
        { id: 3, lat: 37.7649, lng: -122.4294, severity: 0.65, count: 3, date: '2025-01-13' },
        { id: 4, lat: 37.7949, lng: -122.3994, severity: 0.78, count: 4, date: '2025-01-11' },
        { id: 5, lat: 37.7549, lng: -122.4394, severity: 0.55, count: 2, date: '2025-01-14' },
        { id: 6, lat: 37.7899, lng: -122.4144, severity: 0.88, count: 6, date: '2025-01-09' },
        { id: 7, lat: 37.7699, lng: -122.4244, severity: 0.72, count: 4, date: '2025-01-15' },
      ];

      await new Promise(resolve => setTimeout(resolve, 500));
      setAccidents(mockAccidents);
    } catch (error) {
      console.error('Failed to fetch accident data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getHeatColor = (severity) => {
    if (severity >= 0.8) return '#dc2626'; // red-600
    if (severity >= 0.6) return '#f59e0b'; // amber-500
    if (severity >= 0.4) return '#fbbf24'; // amber-400
    return '#fcd34d'; // amber-300
  };

  const getRadius = (count) => {
    return Math.min(count * 3 + 8, 25); // Min 8, max 25
  };

  // Memoize filtered accidents for performance
  const filteredAccidents = useMemo(() => {
    return accidents.filter(accident => {
      if (severityFilter === 'high' && accident.severity < 0.7) return false;
      if (severityFilter === 'medium' && (accident.severity < 0.4 || accident.severity >= 0.7)) return false;
      if (severityFilter === 'low' && accident.severity >= 0.4) return false;
      return true;
    });
  }, [accidents, severityFilter]);

  if (loading) {
    return <LoadingSpinner text="Loading accident heatmap..." />;
  }

  return (
    <div className="h-full w-full">
      {showControls && (
        <div className="absolute top-4 right-4 z-[1000] space-y-2">
          {/* Date Range Filter */}
          <div className="glass rounded-lg p-3 border border-blue-500/30 shadow-lg">
            <div className="flex items-center mb-2 text-white text-sm font-semibold">
              <Calendar className="h-4 w-4 mr-2" />
              Time Range
            </div>
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="w-full bg-slate-800 text-white text-sm rounded px-2 py-1 border border-blue-500/30 focus:outline-none focus:border-cyan-500"
            >
              <option value="all">All Time</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
            </select>
          </div>

          {/* Severity Filter */}
          <div className="glass rounded-lg p-3 border border-blue-500/30 shadow-lg">
            <div className="flex items-center mb-2 text-white text-sm font-semibold">
              <Filter className="h-4 w-4 mr-2" />
              Severity
            </div>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="w-full bg-slate-800 text-white text-sm rounded px-2 py-1 border border-blue-500/30 focus:outline-none focus:border-cyan-500"
            >
              <option value="all">All Levels</option>
              <option value="high">High (70%+)</option>
              <option value="medium">Medium (40-70%)</option>
              <option value="low">Low (&lt;40%)</option>
            </select>
          </div>

          {/* Legend */}
          <div className="glass rounded-lg p-3 border border-blue-500/30 shadow-lg">
            <div className="flex items-center mb-2 text-white text-sm font-semibold">
              <Flame className="h-4 w-4 mr-2" />
              Legend
            </div>
            <div className="space-y-1 text-xs">
              <div className="flex items-center">
                <div className="w-3 h-3 rounded-full bg-red-600 mr-2"></div>
                <span className="text-gray-300">High (80%+)</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 rounded-full bg-amber-500 mr-2"></div>
                <span className="text-gray-300">Medium (60-80%)</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 rounded-full bg-amber-400 mr-2"></div>
                <span className="text-gray-300">Low (40-60%)</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 rounded-full bg-amber-300 mr-2"></div>
                <span className="text-gray-300">Very Low (&lt;40%)</span>
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="glass rounded-lg p-3 border border-blue-500/30 shadow-lg text-center">
            <div className="text-2xl font-bold text-cyan-400">
              {filteredAccidents.length}
            </div>
            <div className="text-xs text-gray-300">Accident Hotspots</div>
          </div>
        </div>
      )}

      <MapContainer
        center={[37.7749, -122.4194]}
        zoom={13}
        className="h-full w-full"
        zoomControl={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <LayerGroup>
          {filteredAccidents.map((accident) => (
            <CircleMarker
              key={accident.id}
              center={[accident.lat, accident.lng]}
              radius={getRadius(accident.count)}
              pathOptions={{
                fillColor: getHeatColor(accident.severity),
                fillOpacity: 0.6,
                color: getHeatColor(accident.severity),
                weight: 2,
                opacity: 0.8,
              }}
            >
              <Popup>
                <div className="text-sm">
                  <div className="font-bold mb-1">Accident Hotspot</div>
                  <div className="text-gray-600">
                    <div>Accidents: {accident.count}</div>
                    <div>Severity: {(accident.severity * 100).toFixed(0)}%</div>
                    <div>Last: {new Date(accident.date).toLocaleDateString()}</div>
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </LayerGroup>
      </MapContainer>
    </div>
  );
});

AccidentHeatmap.displayName = 'AccidentHeatmap';

export default AccidentHeatmap;
