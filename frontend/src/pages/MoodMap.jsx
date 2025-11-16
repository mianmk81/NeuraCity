import { useState, useEffect } from 'react';
import Map2D from '../components/Map2D';
import MoodLegend from '../components/MoodLegend';
import { getMoodData, getIssues } from '../lib/api';
import { Loader2, RefreshCw } from 'lucide-react';

const MoodMap = () => {
  const [moodAreas, setMoodAreas] = useState([]);
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMoodData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [moodData, issuesData] = await Promise.all([
        getMoodData(),
        getIssues({ limit: 1000 })
      ]);
      setMoodAreas(moodData);
      setIssues(issuesData || []);
    } catch (err) {
      setError(err.message || 'Failed to load mood data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMoodData();
    // Refresh data every 30 seconds to show new reports
    const interval = setInterval(fetchMoodData, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen py-4 md:py-8 relative z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-4 md:mb-8">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-white mb-2 neon-blue">
                City Mood Map
              </h1>
              <p className="text-sm md:text-base text-gray-300">
                Emotional sentiment analysis across different city areas
              </p>
            </div>
            <button
              onClick={fetchMoodData}
              disabled={loading}
              className="flex items-center px-4 py-3 btn-futuristic text-white rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed min-h-[44px] w-full sm:w-auto"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 glass border border-red-500/30 rounded-lg p-4">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 md:gap-8">
          {/* Left Panel - Legend and Stats */}
          <div className="lg:col-span-1 space-y-4 md:space-y-6 order-2 lg:order-1">
            <MoodLegend />

            {!loading && moodAreas.length > 0 && (
              <div className="glass rounded-lg shadow p-6 border border-blue-500/30">
                <h3 className="font-semibold text-white mb-4">
                  Area Statistics
                </h3>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-300 mb-1">Total Areas</p>
                    <p className="text-2xl font-bold text-cyan-400">
                      {moodAreas.length}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-300 mb-1">Average Mood</p>
                    <p className={`text-2xl font-bold ${
                      moodAreas.reduce((sum, a) => sum + a.mood_score, 0) / moodAreas.length >= 0.5
                        ? 'text-green-400'
                        : moodAreas.reduce((sum, a) => sum + a.mood_score, 0) / moodAreas.length >= 0
                        ? 'text-yellow-400'
                        : 'text-red-400'
                    }`}>
                      {(moodAreas.reduce((sum, a) => sum + a.mood_score, 0) / moodAreas.length).toFixed(2)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-300 mb-1">Total Posts Analyzed</p>
                    <p className="text-2xl font-bold text-cyan-400">
                      {moodAreas.reduce((sum, a) => sum + (a.post_count || 0), 0)}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {!loading && moodAreas.length > 0 && (
              <div className="glass rounded-lg shadow p-6 border border-blue-500/30">
                <h3 className="font-semibold text-white mb-4">
                  Area Details
                </h3>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {moodAreas
                    .sort((a, b) => b.mood_score - a.mood_score)
                    .map((area, index) => (
                      <div
                        key={area.id || index}
                        className="p-3 glass border border-blue-500/20 rounded-lg hover:border-cyan-500/50 transition-colors"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <p className="font-medium text-white text-sm">
                            {area.area_id || `Area ${index + 1}`}
                          </p>
                          <span
                            className="w-3 h-3 rounded-full shadow-lg"
                            style={{
                              backgroundColor:
                                area.mood_score >= 0.5 ? '#10b981' :
                                area.mood_score >= 0 ? '#fbbf24' : '#ef4444'
                            }}
                          />
                        </div>
                        <div className="text-xs text-gray-300 space-y-1">
                          <p>Mood: {area.mood_score.toFixed(2)}</p>
                          <p>Posts: {area.post_count || 0}</p>
                          <p className="text-gray-400">
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
          <div className="lg:col-span-3 order-1 lg:order-2">
            <div className="glass rounded-lg shadow p-2 md:p-4 border border-blue-500/30">
              <div className="h-[400px] md:h-[500px] lg:h-[700px] xl:h-[800px]">
                {loading ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <Loader2 className="h-12 w-12 text-cyan-400 animate-spin mx-auto mb-4" />
                      <p className="text-gray-300">Loading mood data...</p>
                    </div>
                  </div>
                ) : moodAreas.length === 0 ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <p className="text-gray-300 mb-4">No mood data available</p>
                      <button
                        onClick={fetchMoodData}
                        className="px-4 py-2 btn-futuristic text-white rounded-lg transition-all duration-300"
                      >
                        Try Again
                      </button>
                    </div>
                  </div>
                ) : (
                  <Map2D
                    height="100%"
                    moodAreas={moodAreas}
                    issues={issues}
                    center={[33.7490, -84.3880]} // Atlanta, Georgia
                    zoom={13}
                  />
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MoodMap;
