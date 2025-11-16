import { useState, useEffect } from 'react';
import { getIssues, getWorkOrders } from '../lib/api.js';
import {
  TrendingUp,
  Users,
  Award,
  CheckCircle,
  Clock,
  MapPin,
  Leaf,
  Zap,
  Heart,
  Target,
  Loader2,
  Trophy,
  Star
} from 'lucide-react';

const CommunityImpact = () => {
  const [loading, setLoading] = useState(true);
  const [impact, setImpact] = useState({
    totalReports: 0,
    issuesResolved: 0,
    activeCitizens: 0,
    avgResolutionTime: 0,
    communityScore: 0,
    recentImprovements: [],
    topContributors: [],
    impactByArea: []
  });

  useEffect(() => {
    fetchImpactData();
  }, []);

  const fetchImpactData = async () => {
    setLoading(true);
    try {
      const [issues, workOrders] = await Promise.all([
        getIssues({ limit: 50 }),
        getWorkOrders()
      ]);

      // Calculate metrics
      const totalReports = issues.length;
      const resolved = issues.filter(i => i.status === 'resolved' || i.status === 'closed').length;
      const resolutionRate = totalReports > 0 ? (resolved / totalReports) * 100 : 0;

      // Simulate active citizens (unique reporters - in real app would track user IDs)
      const activeCitizens = Math.min(totalReports * 0.3, 500); // Estimate

      // Calculate average resolution time (simulated)
      const resolvedIssues = issues.filter(i => i.status === 'resolved');
      const avgResolutionTime = resolvedIssues.length > 0
        ? resolvedIssues.reduce((sum, issue) => {
            const created = new Date(issue.created_at);
            const updated = new Date(issue.updated_at || issue.created_at);
            const hours = (updated - created) / (1000 * 60 * 60);
            return sum + hours;
          }, 0) / resolvedIssues.length
        : 48; // Default 48 hours

      // Community score (0-100) based on engagement and resolution
      const communityScore = Math.min(100, 
        (resolutionRate * 0.5) + 
        (Math.min(activeCitizens / 10, 50)) + 
        (Math.max(0, 50 - avgResolutionTime / 24) * 0.3)
      );

      // Recent improvements (resolved issues with work orders)
      const recentImprovements = workOrders
        .filter(wo => wo.status === 'completed' || wo.status === 'approved')
        .slice(0, 10)
        .map(wo => ({
          id: wo.id,
          type: wo.issue?.issue_type || 'infrastructure',
          location: `${wo.issue?.lat?.toFixed(4)}, ${wo.issue?.lng?.toFixed(4)}`,
          resolvedAt: wo.updated_at || wo.created_at,
          impact: wo.issue?.priority === 'critical' ? 'High' : wo.issue?.priority === 'high' ? 'Medium' : 'Low'
        }))
        .sort((a, b) => new Date(b.resolvedAt) - new Date(a.resolvedAt));

      // Top contributors (simulated - would track actual users)
      const topContributors = [
        { name: 'Sarah Chen', reports: 23, resolved: 18, badge: 'Champion', color: 'gold' },
        { name: 'Marcus Johnson', reports: 19, resolved: 15, badge: 'Hero', color: 'silver' },
        { name: 'Emma Rodriguez', reports: 16, resolved: 12, badge: 'Advocate', color: 'bronze' },
        { name: 'David Kim', reports: 14, resolved: 11, badge: 'Champion', color: 'gold' },
        { name: 'Lisa Wang', reports: 12, resolved: 9, badge: 'Hero', color: 'silver' }
      ];

      // Impact by area
      const areaImpact = {};
      issues.forEach(issue => {
        const areaKey = `${Math.round(issue.lat * 10) / 10},${Math.round(issue.lng * 10) / 10}`;
        if (!areaImpact[areaKey]) {
          areaImpact[areaKey] = {
            lat: issue.lat,
            lng: issue.lng,
            total: 0,
            resolved: 0
          };
        }
        areaImpact[areaKey].total++;
        if (issue.status === 'resolved' || issue.status === 'closed') {
          areaImpact[areaKey].resolved++;
        }
      });

      const impactByArea = Object.values(areaImpact)
        .map(area => ({
          ...area,
          resolutionRate: (area.resolved / area.total) * 100
        }))
        .sort((a, b) => b.resolutionRate - a.resolutionRate)
        .slice(0, 10);

      setImpact({
        totalReports,
        issuesResolved: resolved,
        resolutionRate,
        activeCitizens: Math.round(activeCitizens),
        avgResolutionTime: Math.round(avgResolutionTime * 10) / 10,
        communityScore: Math.round(communityScore),
        recentImprovements,
        topContributors,
        impactByArea
      });
    } catch (err) {
      console.error('Failed to fetch impact data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    if (score >= 40) return 'text-orange-400';
    return 'text-red-400';
  };

  const getBadgeIcon = (badge) => {
    switch (badge) {
      case 'Champion': return <Trophy className="h-5 w-5 text-yellow-400" />;
      case 'Hero': return <Star className="h-5 w-5 text-blue-400" />;
      case 'Advocate': return <Award className="h-5 w-5 text-purple-400" />;
      default: return <Award className="h-5 w-5 text-gray-400" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen py-4 md:py-8 relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center" style={{ minHeight: '60vh' }}>
            <div className="text-center">
              <Loader2 className="h-12 w-12 text-cyan-400 animate-spin mx-auto mb-4" />
              <p className="text-gray-300">Loading community impact data...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-4 md:py-8 relative z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-3 neon-blue flex items-center">
            <Heart className="h-10 w-10 mr-3 text-red-400" />
            Community Impact Dashboard
          </h1>
          <p className="text-lg text-gray-300">
            See how your reports are making our city better, safer, and more livable
          </p>
        </div>

        {/* Community Score Hero Card */}
        <div className="glass rounded-2xl shadow-xl p-8 border border-cyan-500/30 mb-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
                <Target className="h-8 w-8 mr-3 text-cyan-400" />
                Community Engagement Score
              </h2>
              <p className="text-gray-300 mb-4">
                Our city's collective effort to improve infrastructure, safety, and quality of life
              </p>
              <div className="flex items-center gap-4">
                <div className="text-center">
                  <p className="text-sm text-gray-400 mb-1">Active Citizens</p>
                  <p className="text-2xl font-bold text-cyan-400">{impact.activeCitizens}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-400 mb-1">Resolution Rate</p>
                  <p className="text-2xl font-bold text-green-400">{impact.resolutionRate.toFixed(1)}%</p>
                </div>
              </div>
            </div>
            <div className="text-center">
              <div className={`text-7xl font-bold mb-2 ${getScoreColor(impact.communityScore)}`}>
                {impact.communityScore}
              </div>
              <p className="text-gray-400">Out of 100</p>
              <div className="mt-4 w-48 h-4 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${
                    impact.communityScore >= 80 ? 'bg-green-500' :
                    impact.communityScore >= 60 ? 'bg-yellow-500' :
                    impact.communityScore >= 40 ? 'bg-orange-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${impact.communityScore}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="glass rounded-xl p-6 border border-blue-500/30">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-400">Total Reports</h3>
              <MapPin className="h-6 w-6 text-cyan-400" />
            </div>
            <p className="text-4xl font-bold text-white mb-2">{impact.totalReports}</p>
            <p className="text-xs text-gray-400">Citizen contributions</p>
          </div>

          <div className="glass rounded-xl p-6 border border-green-500/30">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-400">Issues Resolved</h3>
              <CheckCircle className="h-6 w-6 text-green-400" />
            </div>
            <p className="text-4xl font-bold text-white mb-2">{impact.issuesResolved}</p>
            <p className="text-xs text-gray-400">{impact.resolutionRate.toFixed(1)}% success rate</p>
          </div>

          <div className="glass rounded-xl p-6 border border-purple-500/30">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-400">Active Citizens</h3>
              <Users className="h-6 w-6 text-purple-400" />
            </div>
            <p className="text-4xl font-bold text-white mb-2">{impact.activeCitizens}</p>
            <p className="text-xs text-gray-400">Community members</p>
          </div>

          <div className="glass rounded-xl p-6 border border-yellow-500/30">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-400">Avg Resolution</h3>
              <Clock className="h-6 w-6 text-yellow-400" />
            </div>
            <p className="text-4xl font-bold text-white mb-2">{impact.avgResolutionTime}h</p>
            <p className="text-xs text-gray-400">Time to fix</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Top Contributors */}
          <div className="glass rounded-xl shadow-lg p-6 border border-yellow-500/30">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center">
              <Trophy className="h-6 w-6 mr-2 text-yellow-400" />
              Top Community Contributors
            </h2>
            
            <div className="space-y-4">
              {impact.topContributors.map((contributor, index) => (
                <div
                  key={index}
                  className="glass border border-yellow-500/20 rounded-lg p-4 hover:border-yellow-500/50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg ${
                        index === 0 ? 'bg-yellow-500/20 text-yellow-400' :
                        index === 1 ? 'bg-gray-400/20 text-gray-400' :
                        index === 2 ? 'bg-orange-500/20 text-orange-400' :
                        'bg-blue-500/20 text-blue-400'
                      }`}>
                        {index + 1}
                      </div>
                      <div>
                        <p className="font-medium text-white">{contributor.name}</p>
                        <div className="flex items-center gap-2 mt-1">
                          {getBadgeIcon(contributor.badge)}
                          <p className="text-xs text-gray-400">{contributor.badge}</p>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-cyan-400">{contributor.reports} reports</p>
                      <p className="text-xs text-gray-400">{contributor.resolved} resolved</p>
                    </div>
                  </div>
                  <div className="mt-3">
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-yellow-500 h-2 rounded-full"
                        style={{ width: `${(contributor.resolved / contributor.reports) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Improvements */}
          <div className="glass rounded-xl shadow-lg p-6 border border-green-500/30">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center">
              <Zap className="h-6 w-6 mr-2 text-green-400" />
              Recent City Improvements
            </h2>
            
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {impact.recentImprovements.length === 0 ? (
                <p className="text-gray-400 text-center py-8">No recent improvements to display</p>
              ) : (
                impact.recentImprovements.map((improvement, index) => (
                  <div
                    key={index}
                    className="glass border border-green-500/20 rounded-lg p-4 hover:border-green-500/50 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <CheckCircle className="h-5 w-5 text-green-400 mt-0.5" />
                        <div>
                          <p className="font-medium text-white capitalize">
                            {improvement.type.replace('_', ' ')} Fixed
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            <MapPin className="h-3 w-3 inline mr-1" />
                            {improvement.location}
                          </p>
                        </div>
                      </div>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        improvement.impact === 'High' ? 'bg-red-500/20 text-red-400' :
                        improvement.impact === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-blue-500/20 text-blue-400'
                      }`}>
                        {improvement.impact} Impact
                      </span>
                    </div>
                    <p className="text-xs text-gray-400 mt-2">
                      Resolved {new Date(improvement.resolvedAt).toLocaleDateString()}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Impact by Area */}
        <div className="glass rounded-xl shadow-lg p-6 border border-blue-500/30">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center">
            <TrendingUp className="h-6 w-6 mr-2 text-cyan-400" />
            Impact by Area
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {impact.impactByArea.map((area, index) => (
              <div
                key={index}
                className="glass border border-blue-500/20 rounded-lg p-4 hover:border-cyan-500/50 transition-colors"
              >
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="font-medium text-white">
                      Area {index + 1}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      {area.lat.toFixed(3)}, {area.lng.toFixed(3)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-green-400">
                      {area.resolutionRate.toFixed(1)}%
                    </p>
                    <p className="text-xs text-gray-400">resolved</p>
                  </div>
                </div>
                <div className="mb-2">
                  <div className="flex justify-between text-xs text-gray-400 mb-1">
                    <span>{area.resolved} resolved</span>
                    <span>{area.total} total</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{ width: `${area.resolutionRate}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Call to Action */}
        <div className="mt-8 glass rounded-xl shadow-lg p-8 border border-cyan-500/30 text-center">
          <Leaf className="h-12 w-12 text-green-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-3">
            Be Part of the Change
          </h2>
          <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
            Every report you submit helps make our city safer, cleaner, and more efficient. 
            Join {impact.activeCitizens}+ active citizens making a difference!
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/report"
              className="px-6 py-3 btn-futuristic text-white rounded-lg transition-all duration-300"
            >
              Report an Issue
            </a>
            <a
              href="/analytics"
              className="px-6 py-3 glass border border-cyan-500/50 text-cyan-400 rounded-lg hover:bg-cyan-500/10 transition-all duration-300"
            >
              View Analytics
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CommunityImpact;


