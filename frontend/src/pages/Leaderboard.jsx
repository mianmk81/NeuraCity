import { useState, useEffect } from 'react';
import { Trophy, Medal, Award, Star, TrendingUp, Users } from 'lucide-react';
import { getLeaderboard } from '../lib/api';
import LoadingSpinner from '../components/LoadingSpinner';

const Leaderboard = () => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLeaderboard();
  }, []);

  const fetchLeaderboard = async () => {
    setLoading(true);
    setError(null);
    try {
      // Mock data for now - backend endpoints will be implemented later
      const mockData = [
        { rank: 1, username: 'CityHero', points: 2850, reports: 47, badge: 'gold' },
        { rank: 2, username: 'UrbanGuardian', points: 2340, reports: 39, badge: 'silver' },
        { rank: 3, username: 'StreetWatcher', points: 2100, reports: 35, badge: 'bronze' },
        { rank: 4, username: 'SafetyFirst', points: 1890, reports: 31, badge: null },
        { rank: 5, username: 'CommunityChamp', points: 1650, reports: 28, badge: null },
        { rank: 6, username: 'ReportMaster', points: 1420, reports: 24, badge: null },
        { rank: 7, username: 'CivicStar', points: 1280, reports: 21, badge: null },
        { rank: 8, username: 'NeighborhoodEye', points: 1150, reports: 19, badge: null },
        { rank: 9, username: 'ImpactMaker', points: 980, reports: 16, badge: null },
        { rank: 10, username: 'LocalHero', points: 850, reports: 14, badge: null },
      ];

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 800));
      setLeaderboard(mockData);
    } catch (err) {
      setError(err.message || 'Failed to load leaderboard');
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank) => {
    switch (rank) {
      case 1:
        return <Trophy className="h-6 w-6 text-yellow-400" />;
      case 2:
        return <Medal className="h-6 w-6 text-gray-400" />;
      case 3:
        return <Award className="h-6 w-6 text-orange-400" />;
      default:
        return <Star className="h-5 w-5 text-cyan-400" />;
    }
  };

  const getRankClass = (rank) => {
    switch (rank) {
      case 1:
        return 'bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border-yellow-500/50';
      case 2:
        return 'bg-gradient-to-r from-gray-400/20 to-gray-500/20 border-gray-400/50';
      case 3:
        return 'bg-gradient-to-r from-orange-500/20 to-red-500/20 border-orange-500/50';
      default:
        return 'glass border-blue-500/30';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen py-12 relative z-10">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <LoadingSpinner size="lg" text="Loading leaderboard..." />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen py-12 relative z-10">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="glass rounded-xl p-8 border border-red-500/30">
            <p className="text-red-400">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-12 relative z-10">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12 animate-fade-in-up">
          <div className="flex items-center justify-center mb-6">
            <div className="w-20 h-20 bg-gradient-to-br from-yellow-500 via-orange-500 to-red-500 rounded-2xl flex items-center justify-center shadow-lg glow-box">
              <Trophy className="h-10 w-10 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-white mb-4 neon-blue">
            Community Leaderboard
          </h1>
          <p className="text-gray-300 text-lg">
            Top contributors making our city safer and better
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 animate-fade-in-up stagger-1">
          <div className="glass rounded-xl p-6 border border-blue-500/30 text-center">
            <Users className="h-8 w-8 text-cyan-400 mx-auto mb-3" />
            <div className="text-3xl font-bold text-white mb-1">
              {leaderboard.length}
            </div>
            <div className="text-sm text-gray-300">Active Contributors</div>
          </div>
          <div className="glass rounded-xl p-6 border border-blue-500/30 text-center">
            <TrendingUp className="h-8 w-8 text-green-400 mx-auto mb-3" />
            <div className="text-3xl font-bold text-white mb-1">
              {leaderboard.reduce((sum, user) => sum + user.reports, 0)}
            </div>
            <div className="text-sm text-gray-300">Total Reports</div>
          </div>
          <div className="glass rounded-xl p-6 border border-blue-500/30 text-center">
            <Star className="h-8 w-8 text-yellow-400 mx-auto mb-3" />
            <div className="text-3xl font-bold text-white mb-1">
              {leaderboard.reduce((sum, user) => sum + user.points, 0).toLocaleString()}
            </div>
            <div className="text-sm text-gray-300">Total Points</div>
          </div>
        </div>

        {/* Leaderboard Table */}
        <div className="glass rounded-xl shadow-xl border border-blue-500/30 overflow-hidden animate-fade-in-up stagger-2">
          <div className="p-6 border-b border-blue-500/30">
            <h2 className="text-2xl font-bold text-white">Top 10 Contributors</h2>
          </div>

          <div className="divide-y divide-blue-500/30">
            {leaderboard.map((user, index) => (
              <div
                key={user.rank}
                className={`p-6 flex items-center justify-between hover:bg-blue-500/5 transition-all duration-300 ${getRankClass(user.rank)}`}
                style={{
                  animationDelay: `${index * 50}ms`,
                  animation: 'fadeInUp 0.5s ease-out forwards'
                }}
              >
                <div className="flex items-center space-x-4 flex-1">
                  {/* Rank */}
                  <div className="flex-shrink-0 w-16 flex items-center justify-center">
                    {getRankIcon(user.rank)}
                  </div>

                  {/* Username */}
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <span className="text-lg font-bold text-white">
                        {user.username}
                      </span>
                      {user.badge && (
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                          user.badge === 'gold' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/50' :
                          user.badge === 'silver' ? 'bg-gray-400/20 text-gray-300 border border-gray-400/50' :
                          'bg-orange-500/20 text-orange-400 border border-orange-500/50'
                        }`}>
                          {user.badge.toUpperCase()}
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-400 mt-1">
                      {user.reports} reports submitted
                    </div>
                  </div>

                  {/* Points */}
                  <div className="text-right">
                    <div className="text-2xl font-bold text-cyan-400">
                      {user.points.toLocaleString()}
                    </div>
                    <div className="text-xs text-gray-400">points</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* How to Earn Points */}
        <div className="glass rounded-xl p-6 border border-blue-500/30 mt-8 animate-fade-in-up stagger-3">
          <h3 className="text-xl font-bold text-white mb-4">How to Earn Points</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-green-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-green-400 font-bold">50</span>
              </div>
              <div>
                <div className="text-white font-semibold">Report an Issue</div>
                <div className="text-sm text-gray-400">Submit evidence-based reports</div>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-blue-400 font-bold">100</span>
              </div>
              <div>
                <div className="text-white font-semibold">Critical Issue</div>
                <div className="text-sm text-gray-400">Report high-priority problems</div>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-purple-400 font-bold">25</span>
              </div>
              <div>
                <div className="text-white font-semibold">Issue Resolved</div>
                <div className="text-sm text-gray-400">When your report is fixed</div>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-orange-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-orange-400 font-bold">10</span>
              </div>
              <div>
                <div className="text-white font-semibold">Daily Check-in</div>
                <div className="text-sm text-gray-400">Visit the platform daily</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Leaderboard;
