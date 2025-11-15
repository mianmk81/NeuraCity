import { useState, useEffect } from 'react';
import Map2D from '../components/Map2D';
import MoodLegend from '../components/MoodLegend';
import { getMoodData } from '../lib/api';
import { Loader2, RefreshCw } from 'lucide-react';

const MoodMap = () => {
  const [moodAreas, setMoodAreas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMoodData = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await getMoodData();
      setMoodAreas(data);
    } catch (err) {
      setError(err.message || 'Failed to load mood data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMoodData();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                City Mood Map
              </h1>
              <p className="text-gray-600">
                Emotional sentiment analysis across different city areas
              </p>
            </div>
            <button
              onClick={fetchMoodData}
              disabled={loading}
              className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Left Panel - Legend and Stats */}
          <div className="lg:col-span-1 space-y-6">
            <MoodLegend />

            {!loading && moodAreas.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="font-semibold text-gray-900 mb-4">
                  Area Statistics
                </h3>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Total Areas</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {moodAreas.length}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Average Mood</p>
                    <p className={`text-2xl font-bold ${
                      moodAreas.reduce((sum, a) => sum + a.mood_score, 0) / moodAreas.length >= 0.5
                        ? 'text-green-600'
                        : moodAreas.reduce((sum, a) => sum + a.mood_score, 0) / moodAreas.length >= 0
                        ? 'text-yellow-600'
                        : 'text-red-600'
                    }`}>
                      {(moodAreas.reduce((sum, a) => sum + a.mood_score, 0) / moodAreas.length).toFixed(2)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Total Posts Analyzed</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {moodAreas.reduce((sum, a) => sum + (a.post_count || 0), 0)}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {!loading && moodAreas.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="font-semibold text-gray-900 mb-4">
                  Area Details
                </h3>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {moodAreas
                    .sort((a, b) => b.mood_score - a.mood_score)
                    .map((area, index) => (
                      <div
                        key={area.id || index}
                        className="p-3 border border-gray-200 rounded-lg"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <p className="font-medium text-gray-900 text-sm">
                            {area.area_id || `Area ${index + 1}`}
                          </p>
                          <span
                            className="w-3 h-3 rounded-full"
                            style={{
                              backgroundColor:
                                area.mood_score >= 0.5 ? '#10b981' :
                                area.mood_score >= 0 ? '#fbbf24' : '#ef4444'
                            }}
                          />
                        </div>
                        <div className="text-xs text-gray-600 space-y-1">
                          <p>Mood: {area.mood_score.toFixed(2)}</p>
                          <p>Posts: {area.post_count || 0}</p>
                          <p className="text-gray-500">
                            {area.lat.toFixed(4)}, {area.lng.toFixed(4)}
                          </p>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Panel - Map */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow p-4">
              {loading ? (
                <div className="flex items-center justify-center" style={{ height: 'calc(100vh - 200px)' }}>
                  <div className="text-center">
                    <Loader2 className="h-12 w-12 text-primary-600 animate-spin mx-auto mb-4" />
                    <p className="text-gray-600">Loading mood data...</p>
                  </div>
                </div>
              ) : moodAreas.length === 0 ? (
                <div className="flex items-center justify-center" style={{ height: 'calc(100vh - 200px)' }}>
                  <div className="text-center">
                    <p className="text-gray-600 mb-4">No mood data available</p>
                    <button
                      onClick={fetchMoodData}
                      className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                    >
                      Try Again
                    </button>
                  </div>
                </div>
              ) : (
                <Map2D
                  height="calc(100vh - 200px)"
                  moodAreas={moodAreas}
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MoodMap;
