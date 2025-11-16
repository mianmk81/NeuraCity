import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Rectangle, Popup, Tooltip } from 'react-leaflet';
import { Shield, AlertTriangle, Wind, Activity, Car, Volume2, Info } from 'lucide-react';
import { getRiskIndex, getAreaRiskDetails } from '../lib/api';
import LoadingSpinner from '../components/LoadingSpinner';
import 'leaflet/dist/leaflet.css';

const RiskIndex = () => {
  const [riskData, setRiskData] = useState([]);
  const [selectedArea, setSelectedArea] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRiskData();
  }, []);

  const fetchRiskData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Mock data for risk index - backend will implement later
      const mockData = [
        {
          id: 'area-1',
          name: 'Downtown',
          bounds: [[37.785, -122.41], [37.795, -122.40]],
          risk_score: 0.72,
          crime_score: 0.65,
          air_quality: 0.78,
          accident_rate: 0.82,
          noise_level: 0.75,
        },
        {
          id: 'area-2',
          name: 'Park District',
          bounds: [[37.775, -122.45], [37.785, -122.44]],
          risk_score: 0.25,
          crime_score: 0.15,
          air_quality: 0.20,
          accident_rate: 0.35,
          noise_level: 0.30,
        },
        {
          id: 'area-3',
          name: 'Industrial Zone',
          bounds: [[37.765, -122.40], [37.775, -122.39]],
          risk_score: 0.85,
          crime_score: 0.55,
          air_quality: 0.95,
          accident_rate: 0.88,
          noise_level: 0.92,
        },
        {
          id: 'area-4',
          name: 'Residential',
          bounds: [[37.755, -122.45], [37.765, -122.44]],
          risk_score: 0.35,
          crime_score: 0.25,
          air_quality: 0.40,
          accident_rate: 0.38,
          noise_level: 0.35,
        },
        {
          id: 'area-5',
          name: 'Campus',
          bounds: [[37.795, -122.42], [37.805, -122.41]],
          risk_score: 0.42,
          crime_score: 0.30,
          air_quality: 0.35,
          accident_rate: 0.55,
          noise_level: 0.48,
        },
        {
          id: 'area-6',
          name: 'Waterfront',
          bounds: [[37.745, -122.40], [37.755, -122.39]],
          risk_score: 0.58,
          crime_score: 0.45,
          air_quality: 0.50,
          accident_rate: 0.70,
          noise_level: 0.65,
        },
      ];

      await new Promise(resolve => setTimeout(resolve, 800));
      setRiskData(mockData);
    } catch (err) {
      setError(err.message || 'Failed to load risk index');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (score) => {
    if (score >= 0.7) return '#ef4444'; // red
    if (score >= 0.5) return '#f59e0b'; // orange
    if (score >= 0.3) return '#eab308'; // yellow
    return '#22c55e'; // green
  };

  const getRiskLevel = (score) => {
    if (score >= 0.7) return 'High Risk';
    if (score >= 0.5) return 'Moderate Risk';
    if (score >= 0.3) return 'Low Risk';
    return 'Very Low Risk';
  };

  const getRiskClass = (score) => {
    if (score >= 0.7) return 'text-red-400 bg-red-500/20 border-red-500/50';
    if (score >= 0.5) return 'text-orange-400 bg-orange-500/20 border-orange-500/50';
    if (score >= 0.3) return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/50';
    return 'text-green-400 bg-green-500/20 border-green-500/50';
  };

  if (loading) {
    return (
      <div className="min-h-screen py-12 relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <LoadingSpinner size="lg" text="Loading risk index..." />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen py-12 relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="glass rounded-xl p-8 border border-red-500/30">
            <p className="text-red-400">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-12 relative z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 animate-fade-in-up">
          <div className="flex items-center mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-orange-500 rounded-xl flex items-center justify-center shadow-lg glow-box mr-4">
              <Shield className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white neon-blue">
                Community Risk Index
              </h1>
              <p className="text-gray-300">
                Safety metrics across different city areas
              </p>
            </div>
          </div>
        </div>

        {/* Map and Details Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Map */}
          <div className="lg:col-span-2 glass rounded-xl shadow-lg border border-blue-500/30 overflow-hidden animate-fade-in-up">
            <div className="h-[600px] relative">
              <MapContainer
                center={[37.7749, -122.4194]}
                zoom={12}
                className="h-full w-full"
                zoomControl={true}
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {riskData.map((area) => (
                  <Rectangle
                    key={area.id}
                    bounds={area.bounds}
                    pathOptions={{
                      color: getRiskColor(area.risk_score),
                      fillColor: getRiskColor(area.risk_score),
                      fillOpacity: 0.4,
                      weight: 2,
                    }}
                    eventHandlers={{
                      click: () => setSelectedArea(area),
                    }}
                  >
                    <Tooltip direction="top" offset={[0, -10]} opacity={0.9}>
                      <div className="text-sm">
                        <div className="font-bold">{area.name}</div>
                        <div>Risk: {(area.risk_score * 100).toFixed(0)}%</div>
                      </div>
                    </Tooltip>
                  </Rectangle>
                ))}
              </MapContainer>
            </div>
          </div>

          {/* Risk Legend and Info */}
          <div className="space-y-6 animate-fade-in-up stagger-1">
            {/* Legend */}
            <div className="glass rounded-xl p-6 border border-blue-500/30">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center">
                <Info className="h-5 w-5 mr-2 text-cyan-400" />
                Risk Levels
              </h3>
              <div className="space-y-3">
                {[
                  { level: 'Very Low Risk', color: '#22c55e', range: '0-30%' },
                  { level: 'Low Risk', color: '#eab308', range: '30-50%' },
                  { level: 'Moderate Risk', color: '#f59e0b', range: '50-70%' },
                  { level: 'High Risk', color: '#ef4444', range: '70-100%' },
                ].map((item) => (
                  <div key={item.level} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div
                        className="w-4 h-4 rounded"
                        style={{ backgroundColor: item.color }}
                      ></div>
                      <span className="text-sm text-gray-300">{item.level}</span>
                    </div>
                    <span className="text-xs text-gray-400">{item.range}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Selected Area Details */}
            {selectedArea ? (
              <div className="glass rounded-xl p-6 border border-blue-500/30">
                <h3 className="text-lg font-bold text-white mb-4">{selectedArea.name}</h3>

                <div className={`px-3 py-2 rounded-lg border mb-4 ${getRiskClass(selectedArea.risk_score)}`}>
                  <div className="text-sm font-semibold">
                    {getRiskLevel(selectedArea.risk_score)}
                  </div>
                  <div className="text-2xl font-bold">
                    {(selectedArea.risk_score * 100).toFixed(0)}%
                  </div>
                </div>

                <div className="space-y-3">
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center text-sm text-gray-300">
                        <AlertTriangle className="h-4 w-4 mr-2" />
                        Crime Rate
                      </div>
                      <span className="text-sm font-semibold text-white">
                        {(selectedArea.crime_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className="h-2 rounded-full"
                        style={{
                          width: `${selectedArea.crime_score * 100}%`,
                          backgroundColor: getRiskColor(selectedArea.crime_score),
                        }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center text-sm text-gray-300">
                        <Wind className="h-4 w-4 mr-2" />
                        Air Quality
                      </div>
                      <span className="text-sm font-semibold text-white">
                        {(selectedArea.air_quality * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className="h-2 rounded-full"
                        style={{
                          width: `${selectedArea.air_quality * 100}%`,
                          backgroundColor: getRiskColor(selectedArea.air_quality),
                        }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center text-sm text-gray-300">
                        <Car className="h-4 w-4 mr-2" />
                        Accident Rate
                      </div>
                      <span className="text-sm font-semibold text-white">
                        {(selectedArea.accident_rate * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className="h-2 rounded-full"
                        style={{
                          width: `${selectedArea.accident_rate * 100}%`,
                          backgroundColor: getRiskColor(selectedArea.accident_rate),
                        }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center text-sm text-gray-300">
                        <Volume2 className="h-4 w-4 mr-2" />
                        Noise Level
                      </div>
                      <span className="text-sm font-semibold text-white">
                        {(selectedArea.noise_level * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className="h-2 rounded-full"
                        style={{
                          width: `${selectedArea.noise_level * 100}%`,
                          backgroundColor: getRiskColor(selectedArea.noise_level),
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="glass rounded-xl p-6 border border-blue-500/30 text-center">
                <Activity className="h-12 w-12 text-gray-500 mx-auto mb-3" />
                <p className="text-gray-400 text-sm">
                  Click on a colored area to view detailed risk breakdown
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Risk Areas Summary */}
        <div className="mt-8 glass rounded-xl p-6 border border-blue-500/30 animate-fade-in-up stagger-2">
          <h3 className="text-xl font-bold text-white mb-6">All Areas Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {riskData.map((area) => (
              <div
                key={area.id}
                className={`p-4 rounded-lg border cursor-pointer hover:scale-105 transition-transform duration-300 ${getRiskClass(area.risk_score)}`}
                onClick={() => setSelectedArea(area)}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-white">{area.name}</span>
                  <Shield className="h-4 w-4" />
                </div>
                <div className="text-2xl font-bold">
                  {(area.risk_score * 100).toFixed(0)}%
                </div>
                <div className="text-xs opacity-80">
                  {getRiskLevel(area.risk_score)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskIndex;
