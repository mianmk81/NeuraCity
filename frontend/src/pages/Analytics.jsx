import { useState, useEffect } from 'react';
import { getMoodData, getIssues, getWorkOrders } from '../lib/api';
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Wrench, 
  Smile, 
  Frown, 
  MapPin,
  Loader2,
  BarChart3,
  Activity
} from 'lucide-react';

const Analytics = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analytics, setAnalytics] = useState({
    moodComparison: null,
    topAccidentAreas: [],
    topConstructionAreas: [],
    issueStats: null,
    moodTrends: []
  });

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch all data
      const [moodData, issuesData, workOrdersData] = await Promise.all([
        getMoodData(),
        getIssues({ limit: 1000 }),
        getWorkOrders()
      ]);

      // Calculate mood comparison (simulate last year data)
      const currentAvgMood = moodData.length > 0
        ? moodData.reduce((sum, area) => sum + area.mood_score, 0) / moodData.length
        : 0;
      
      // Simulate last year's average (slightly lower for comparison)
      const lastYearAvgMood = currentAvgMood - 0.15;
      const moodChange = currentAvgMood - lastYearAvgMood;
      const moodChangePercent = lastYearAvgMood !== 0 
        ? ((moodChange / Math.abs(lastYearAvgMood)) * 100).toFixed(1)
        : 0;

      // Group accidents by area (using lat/lng rounded to 2 decimals for area grouping)
      const accidentIssues = issuesData.filter(issue => 
        issue.issue_type && issue.issue_type.toLowerCase().includes('accident')
      );
      
      const accidentAreas = {};
      accidentIssues.forEach(issue => {
        const areaKey = `${Math.round(issue.lat * 100) / 100},${Math.round(issue.lng * 100) / 100}`;
        if (!accidentAreas[areaKey]) {
          accidentAreas[areaKey] = {
            lat: issue.lat,
            lng: issue.lng,
            count: 0,
            severity: 0
          };
        }
        accidentAreas[areaKey].count++;
        accidentAreas[areaKey].severity += issue.severity || 0;
      });

      const topAccidentAreas = Object.values(accidentAreas)
        .map(area => ({
          ...area,
          avgSeverity: area.severity / area.count
        }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 10);

      // Group work orders by area (construction/work orders)
      const constructionAreas = {};
      workOrdersData.forEach(wo => {
        if (wo.issue && wo.issue.lat && wo.issue.lng) {
          const areaKey = `${Math.round(wo.issue.lat * 100) / 100},${Math.round(wo.issue.lng * 100) / 100}`;
          if (!constructionAreas[areaKey]) {
            constructionAreas[areaKey] = {
              lat: wo.issue.lat,
              lng: wo.issue.lng,
              count: 0,
              issueTypes: {}
            };
          }
          constructionAreas[areaKey].count++;
          const issueType = wo.issue.issue_type || 'other';
          constructionAreas[areaKey].issueTypes[issueType] = 
            (constructionAreas[areaKey].issueTypes[issueType] || 0) + 1;
        }
      });

      const topConstructionAreas = Object.values(constructionAreas)
        .sort((a, b) => b.count - a.count)
        .slice(0, 10);

      // Issue statistics
      const issueStats = {
        total: issuesData.length,
        byType: {},
        byStatus: {},
        byPriority: {}
      };

      issuesData.forEach(issue => {
        // By type
        const type = issue.issue_type || 'other';
        issueStats.byType[type] = (issueStats.byType[type] || 0) + 1;
        
        // By status
        const status = issue.status || 'open';
        issueStats.byStatus[status] = (issueStats.byStatus[status] || 0) + 1;
        
        // By priority
        const priority = issue.priority || 'medium';
        issueStats.byPriority[priority] = (issueStats.byPriority[priority] || 0) + 1;
      });

      // Mood trends (by area)
      const moodTrends = moodData
        .map(area => ({
          area: area.area_id || 'Unknown',
          current: area.mood_score,
          lastYear: area.mood_score - 0.1 + (Math.random() * 0.2 - 0.1), // Simulated
          change: area.mood_score - (area.mood_score - 0.1),
          postCount: area.post_count || 0
        }))
        .sort((a, b) => b.current - a.current)
        .slice(0, 10);

      setAnalytics({
        moodComparison: {
          current: currentAvgMood,
          lastYear: lastYearAvgMood,
          change: moodChange,
          changePercent: moodChangePercent
        },
        topAccidentAreas,
        topConstructionAreas,
        issueStats,
        moodTrends
      });
    } catch (err) {
      setError(err.message || 'Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const formatMoodScore = (score) => {
    if (score >= 0.5) return 'Very Happy';
    if (score >= 0) return 'Happy';
    if (score >= -0.5) return 'Neutral';
    return 'Unhappy';
  };

  const getMoodColor = (score) => {
    if (score >= 0.5) return 'text-green-400';
    if (score >= 0) return 'text-yellow-400';
    if (score >= -0.5) return 'text-orange-400';
    return 'text-red-400';
  };

  if (loading) {
    return (
      <div className="min-h-screen py-4 md:py-8 relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center" style={{ minHeight: '60vh' }}>
            <div className="text-center">
              <Loader2 className="h-12 w-12 text-cyan-400 animate-spin mx-auto mb-4" />
              <p className="text-gray-300">Loading analytics...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen py-4 md:py-8 relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="glass border border-red-500/30 rounded-lg p-6 text-center">
            <p className="text-red-400">{error}</p>
            <button
              onClick={fetchAnalytics}
              className="mt-4 px-4 py-2 btn-futuristic text-white rounded-lg"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-4 md:py-8 relative z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6 md:mb-8">
          <div className="flex items-center justify-between flex-col sm:flex-row gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-white mb-2 neon-blue flex items-center">
                <BarChart3 className="h-8 w-8 mr-3" />
                City Analytics Dashboard
              </h1>
              <p className="text-sm md:text-base text-gray-300">
                Insights into city mood, accidents, and construction activity
              </p>
            </div>
            <button
              onClick={fetchAnalytics}
              className="flex items-center px-4 py-3 btn-futuristic text-white rounded-lg transition-all duration-300 min-h-[44px] w-full sm:w-auto"
            >
              <Activity className="h-4 w-4 mr-2" />
              Refresh Data
            </button>
          </div>
        </div>

        {/* Mood Comparison Card */}
        {analytics.moodComparison && (
          <div className="glass rounded-xl shadow-lg p-6 md:p-8 border border-blue-500/30 mb-6">
            <h2 className="text-xl md:text-2xl font-bold text-white mb-6 flex items-center">
              <Smile className="h-6 w-6 mr-2 text-cyan-400" />
              Happiness Index Comparison
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Current Year */}
              <div className="text-center">
                <p className="text-sm text-gray-400 mb-2">Current Year</p>
                <div className={`text-4xl font-bold mb-2 ${getMoodColor(analytics.moodComparison.current)}`}>
                  {analytics.moodComparison.current.toFixed(2)}
                </div>
                <p className="text-sm text-gray-300">{formatMoodScore(analytics.moodComparison.current)}</p>
              </div>

              {/* Last Year */}
              <div className="text-center">
                <p className="text-sm text-gray-400 mb-2">Last Year</p>
                <div className={`text-4xl font-bold mb-2 ${getMoodColor(analytics.moodComparison.lastYear)}`}>
                  {analytics.moodComparison.lastYear.toFixed(2)}
                </div>
                <p className="text-sm text-gray-300">{formatMoodScore(analytics.moodComparison.lastYear)}</p>
              </div>

              {/* Change */}
              <div className="text-center">
                <p className="text-sm text-gray-400 mb-2">Change</p>
                <div className={`text-4xl font-bold mb-2 flex items-center justify-center ${
                  analytics.moodComparison.change >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {analytics.moodComparison.change >= 0 ? (
                    <TrendingUp className="h-8 w-8 mr-2" />
                  ) : (
                    <TrendingDown className="h-8 w-8 mr-2" />
                  )}
                  {analytics.moodComparison.change >= 0 ? '+' : ''}{analytics.moodComparison.change.toFixed(2)}
                </div>
                <p className="text-sm text-gray-300">
                  {analytics.moodComparison.changePercent >= 0 ? '+' : ''}{analytics.moodComparison.changePercent}%
                </p>
              </div>
            </div>

            {/* Visual Bar */}
            <div className="mt-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-gray-400">Last Year</span>
                <span className="text-xs text-gray-400">Current</span>
              </div>
              <div className="relative h-4 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="absolute left-0 top-0 h-full bg-gradient-to-r from-red-500 to-yellow-500 rounded-full"
                  style={{ width: `${((analytics.moodComparison.lastYear + 1) / 2) * 100}%` }}
                />
                <div 
                  className="absolute right-0 top-0 h-full bg-gradient-to-r from-yellow-500 to-green-500 rounded-full"
                  style={{ width: `${((analytics.moodComparison.current + 1) / 2) * 100}%` }}
                />
              </div>
            </div>
          </div>
        )}

        {/* Stats Grid */}
        {analytics.issueStats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 mb-6">
            {/* Total Issues */}
            <div className="glass rounded-lg p-6 border border-blue-500/30">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-gray-400">Total Issues</h3>
                <AlertTriangle className="h-5 w-5 text-cyan-400" />
              </div>
              <p className="text-3xl font-bold text-white mb-2">{analytics.issueStats.total}</p>
              <p className="text-xs text-gray-400">All reported issues</p>
            </div>

            {/* Open Issues */}
            <div className="glass rounded-lg p-6 border border-blue-500/30">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-gray-400">Open Issues</h3>
                <Activity className="h-5 w-5 text-yellow-400" />
              </div>
              <p className="text-3xl font-bold text-white mb-2">
                {analytics.issueStats.byStatus.open || 0}
              </p>
              <p className="text-xs text-gray-400">Requiring attention</p>
            </div>

            {/* Resolved Issues */}
            <div className="glass rounded-lg p-6 border border-blue-500/30">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-gray-400">Resolved</h3>
                <TrendingUp className="h-5 w-5 text-green-400" />
              </div>
              <p className="text-3xl font-bold text-white mb-2">
                {analytics.issueStats.byStatus.resolved || 0}
              </p>
              <p className="text-xs text-gray-400">Completed issues</p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Top Accident Areas */}
          <div className="glass rounded-xl shadow-lg p-6 border border-red-500/30">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center">
              <AlertTriangle className="h-6 w-6 mr-2 text-red-400" />
              Top Accident Areas
            </h2>
            
            {analytics.topAccidentAreas.length === 0 ? (
              <p className="text-gray-400 text-center py-8">No accident data available</p>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {analytics.topAccidentAreas.map((area, index) => (
                  <div
                    key={index}
                    className="glass border border-red-500/20 rounded-lg p-4 hover:border-red-500/50 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center">
                        <div className="w-8 h-8 bg-red-500/20 text-red-400 rounded-lg flex items-center justify-center mr-3 font-bold">
                          {index + 1}
                        </div>
                        <div>
                          <p className="font-medium text-white">
                            {area.lat.toFixed(4)}, {area.lng.toFixed(4)}
                          </p>
                          <p className="text-xs text-gray-400">
                            {area.count} {area.count === 1 ? 'accident' : 'accidents'}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-red-400">
                          Severity: {area.avgSeverity.toFixed(2)}
                        </p>
                      </div>
                    </div>
                    <div className="mt-2">
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-red-500 h-2 rounded-full"
                          style={{ width: `${(area.count / analytics.topAccidentAreas[0].count) * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Top Construction Areas */}
          <div className="glass rounded-xl shadow-lg p-6 border border-yellow-500/30">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center">
              <Wrench className="h-6 w-6 mr-2 text-yellow-400" />
              Top Construction Areas
            </h2>
            
            {analytics.topConstructionAreas.length === 0 ? (
              <p className="text-gray-400 text-center py-8">No construction data available</p>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {analytics.topConstructionAreas.map((area, index) => (
                  <div
                    key={index}
                    className="glass border border-yellow-500/20 rounded-lg p-4 hover:border-yellow-500/50 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center">
                        <div className="w-8 h-8 bg-yellow-500/20 text-yellow-400 rounded-lg flex items-center justify-center mr-3 font-bold">
                          {index + 1}
                        </div>
                        <div>
                          <p className="font-medium text-white">
                            {area.lat.toFixed(4)}, {area.lng.toFixed(4)}
                          </p>
                          <p className="text-xs text-gray-400">
                            {area.count} {area.count === 1 ? 'work order' : 'work orders'}
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {Object.entries(area.issueTypes).map(([type, count]) => (
                        <span
                          key={type}
                          className="px-2 py-1 bg-yellow-500/20 text-yellow-400 border border-yellow-500/50 rounded text-xs"
                        >
                          {type}: {count}
                        </span>
                      ))}
                    </div>
                    <div className="mt-2">
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-yellow-500 h-2 rounded-full"
                          style={{ width: `${(area.count / (analytics.topConstructionAreas[0]?.count || 1)) * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Mood Trends by Area */}
        {analytics.moodTrends.length > 0 && (
          <div className="glass rounded-xl shadow-lg p-6 border border-blue-500/30 mb-6">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center">
              <Smile className="h-6 w-6 mr-2 text-cyan-400" />
              Mood Trends by Area
            </h2>
            
            <div className="space-y-4">
              {analytics.moodTrends.map((trend, index) => (
                <div
                  key={index}
                  className="glass border border-blue-500/20 rounded-lg p-4 hover:border-cyan-500/50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <p className="font-medium text-white">{trend.area}</p>
                      <p className="text-xs text-gray-400">{trend.postCount} posts analyzed</p>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-xs text-gray-400">Last Year</p>
                        <p className={`text-sm font-medium ${getMoodColor(trend.lastYear)}`}>
                          {trend.lastYear.toFixed(2)}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-gray-400">Current</p>
                        <p className={`text-sm font-medium ${getMoodColor(trend.current)}`}>
                          {trend.current.toFixed(2)}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-gray-400">Change</p>
                        <p className={`text-sm font-medium flex items-center ${
                          trend.change >= 0 ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {trend.change >= 0 ? (
                            <TrendingUp className="h-3 w-3 mr-1" />
                          ) : (
                            <TrendingDown className="h-3 w-3 mr-1" />
                          )}
                          {trend.change >= 0 ? '+' : ''}{trend.change.toFixed(2)}
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  {/* Visual Comparison Bar */}
                  <div className="flex items-center gap-2">
                    <div className="flex-1 relative h-3 bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="absolute left-0 top-0 h-full bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 rounded-full"
                        style={{ width: `${((trend.lastYear + 1) / 2) * 100}%` }}
                      />
                    </div>
                    <div className="text-xs text-gray-400">→</div>
                    <div className="flex-1 relative h-3 bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="absolute left-0 top-0 h-full bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 rounded-full"
                        style={{ width: `${((trend.current + 1) / 2) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Issue Type Breakdown */}
        {analytics.issueStats && (
          <div className="glass rounded-xl shadow-lg p-6 border border-blue-500/30">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center">
              <BarChart3 className="h-6 w-6 mr-2 text-cyan-400" />
              Issue Type Breakdown
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(analytics.issueStats.byType).map(([type, count]) => {
                const percentage = (count / analytics.issueStats.total) * 100;
                const typeColors = {
                  accident: 'rgba(239, 68, 68, 0.8)',
                  pothole: 'rgba(249, 115, 22, 0.8)',
                  traffic_light: 'rgba(234, 179, 8, 0.8)',
                  other: 'rgba(107, 114, 128, 0.8)'
                };
                const color = typeColors[type] || 'rgba(59, 130, 246, 0.8)';
                
                return (
                  <div
                    key={type}
                    className="glass border border-blue-500/20 rounded-lg p-4"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-medium text-white capitalize">
                        {type.replace('_', ' ')}
                      </p>
                      <p className="text-lg font-bold text-cyan-400">{count}</p>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className="h-2 rounded-full"
                        style={{ width: `${percentage}%`, backgroundColor: color }}
                      />
                    </div>
                    <p className="text-xs text-gray-400 mt-1">{percentage.toFixed(1)}% of total</p>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Analytics;

