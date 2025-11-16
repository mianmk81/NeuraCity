import { useState, useEffect } from 'react';
import { getIssues, getTrafficData, planRoute } from '../lib/api';
import {
  Leaf,
  Droplet,
  Wind,
  TrendingDown,
  TrendingUp,
  Activity,
  Car,
  Footprints,
  Recycle,
  Zap,
  Loader2,
  Award,
  Target
} from 'lucide-react';

const Sustainability = () => {
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState({
    totalCO2Saved: 0,
    ecoRoutesTaken: 0,
    walkingRoutes: 0,
    waterSaved: 0,
    energyEfficiency: 0,
    sustainabilityScore: 0,
    carbonFootprint: 0,
    weeklyTrend: [],
    topEcoAreas: []
  });

  useEffect(() => {
    fetchSustainabilityData();
  }, []);

  const fetchSustainabilityData = async () => {
    setLoading(true);
    try {
      const [issues, traffic] = await Promise.all([
        getIssues({ limit: 50 }),
        getTrafficData()
      ]);

      // Calculate CO2 saved from eco routes (simulated)
      const ecoRoutes = Math.floor(issues.length * 0.15); // 15% use eco routes
      const avgDistance = 5.2; // km
      const co2PerKm = 0.12; // kg CO2 per km (eco route)
      const standardCO2PerKm = 0.15; // kg CO2 per km (standard)
      const co2SavedPerRoute = (standardCO2PerKm - co2PerKm) * avgDistance;
      const totalCO2Saved = ecoRoutes * co2SavedPerRoute;

      // Walking routes
      const walkingRoutes = Math.floor(issues.length * 0.08); // 8% walk

      // Water saved from infrastructure improvements (simulated)
      const infrastructureIssues = issues.filter(i => 
        i.issue_type === 'pothole' || i.issue_type === 'traffic_light'
      );
      const waterSaved = infrastructureIssues.length * 1250; // liters per fix

      // Energy efficiency (based on traffic optimization)
      const avgCongestion = traffic.length > 0
        ? traffic.reduce((sum, t) => sum + (t.congestion || 0), 0) / traffic.length
        : 0.5;
      const energyEfficiency = Math.max(0, (1 - avgCongestion) * 100);

      // Sustainability score (0-100)
      const sustainabilityScore = Math.min(100,
        (totalCO2Saved / 100) * 30 + // CO2 savings component
        (walkingRoutes / 10) * 25 + // Walking encouragement
        (energyEfficiency / 100) * 25 + // Energy efficiency
        (waterSaved / 10000) * 20 // Water conservation
      );

      // Carbon footprint (kg CO2)
      const totalDrives = issues.length * 0.77; // 77% drive
      const carbonFootprint = totalDrives * avgDistance * standardCO2PerKm;

      // Weekly trend (simulated)
      const weeklyTrend = Array.from({ length: 7 }, (_, i) => ({
        day: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i],
        co2Saved: totalCO2Saved / 7 + (Math.random() * 20 - 10),
        ecoRoutes: Math.floor(ecoRoutes / 7) + Math.floor(Math.random() * 3)
      }));

      // Top eco areas (areas with most eco routes)
      const areaEco = {};
      issues.forEach(issue => {
        const areaKey = `${Math.round(issue.lat * 10) / 10},${Math.round(issue.lng * 10) / 10}`;
        if (!areaEco[areaKey]) {
          areaEco[areaKey] = {
            lat: issue.lat,
            lng: issue.lng,
            ecoRoutes: 0,
            totalRoutes: 0
          };
        }
        areaEco[areaKey].totalRoutes++;
        if (Math.random() < 0.15) { // 15% eco route probability
          areaEco[areaKey].ecoRoutes++;
        }
      });

      const topEcoAreas = Object.values(areaEco)
        .map(area => ({
          ...area,
          ecoPercentage: (area.ecoRoutes / area.totalRoutes) * 100
        }))
        .filter(area => area.totalRoutes >= 3)
        .sort((a, b) => b.ecoPercentage - a.ecoPercentage)
        .slice(0, 10);

      setMetrics({
        totalCO2Saved: Math.round(totalCO2Saved * 10) / 10,
        ecoRoutesTaken: ecoRoutes,
        walkingRoutes,
        waterSaved: Math.round(waterSaved),
        energyEfficiency: Math.round(energyEfficiency * 10) / 10,
        sustainabilityScore: Math.round(sustainabilityScore),
        carbonFootprint: Math.round(carbonFootprint * 10) / 10,
        weeklyTrend,
        topEcoAreas
      });
    } catch (err) {
      console.error('Failed to fetch sustainability data:', err);
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

  if (loading) {
    return (
      <div className="min-h-screen py-4 md:py-8 relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center" style={{ minHeight: '60vh' }}>
            <div className="text-center">
              <Loader2 className="h-12 w-12 text-green-400 animate-spin mx-auto mb-4" />
              <p className="text-gray-300">Loading sustainability metrics...</p>
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
            <Leaf className="h-10 w-10 mr-3 text-green-400" />
            Sustainability Dashboard
          </h1>
          <p className="text-lg text-gray-300">
            Track our city's environmental impact and carbon footprint reduction
          </p>
        </div>

        {/* Sustainability Score Hero */}
        <div className="glass rounded-2xl shadow-xl p-8 border border-green-500/30 mb-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
                <Target className="h-8 w-8 mr-3 text-green-400" />
                City Sustainability Score
              </h2>
              <p className="text-gray-300 mb-4">
                Our collective effort to reduce carbon emissions, conserve resources, and promote eco-friendly transportation
              </p>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-400 mb-1">CO₂ Saved</p>
                  <p className="text-xl font-bold text-green-400">{metrics.totalCO2Saved} kg</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400 mb-1">Eco Routes</p>
                  <p className="text-xl font-bold text-cyan-400">{metrics.ecoRoutesTaken}</p>
                </div>
              </div>
            </div>
            <div className="text-center">
              <div className={`text-7xl font-bold mb-2 ${getScoreColor(metrics.sustainabilityScore)}`}>
                {metrics.sustainabilityScore}
              </div>
              <p className="text-gray-400">Out of 100</p>
              <div className="mt-4 w-48 h-4 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${
                    metrics.sustainabilityScore >= 80 ? 'bg-green-500' :
                    metrics.sustainabilityScore >= 60 ? 'bg-yellow-500' :
                    metrics.sustainabilityScore >= 40 ? 'bg-orange-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${metrics.sustainabilityScore}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="glass rounded-xl p-6 border border-green-500/30">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-400">CO₂ Saved</h3>
              <Wind className="h-6 w-6 text-green-400" />
            </div>
            <p className="text-4xl font-bold text-white mb-2">{metrics.totalCO2Saved} kg</p>
            <p className="text-xs text-gray-400">From eco routes</p>
            <div className="mt-2 flex items-center text-green-400">
              <TrendingDown className="h-4 w-4 mr-1" />
              <span className="text-xs">Reduced emissions</span>
            </div>
          </div>

          <div className="glass rounded-xl p-6 border border-cyan-500/30">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-400">Eco Routes</h3>
              <Car className="h-6 w-6 text-cyan-400" />
            </div>
            <p className="text-4xl font-bold text-white mb-2">{metrics.ecoRoutesTaken}</p>
            <p className="text-xs text-gray-400">Low-emission trips</p>
          </div>

          <div className="glass rounded-xl p-6 border border-blue-500/30">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-400">Walking Routes</h3>
              <Footprints className="h-6 w-6 text-blue-400" />
            </div>
            <p className="text-4xl font-bold text-white mb-2">{metrics.walkingRoutes}</p>
            <p className="text-xs text-gray-400">Zero-emission trips</p>
          </div>

          <div className="glass rounded-xl p-6 border border-purple-500/30">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-400">Water Saved</h3>
              <Droplet className="h-6 w-6 text-purple-400" />
            </div>
            <p className="text-4xl font-bold text-white mb-2">{Math.round(metrics.waterSaved / 1000)}k L</p>
            <p className="text-xs text-gray-400">From infrastructure fixes</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Weekly Trend */}
          <div className="glass rounded-xl shadow-lg p-6 border border-green-500/30">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center">
              <Activity className="h-6 w-6 mr-2 text-green-400" />
              Weekly CO₂ Savings Trend
            </h2>
            
            <div className="space-y-4">
              {metrics.weeklyTrend.map((day, index) => (
                <div key={index} className="glass border border-green-500/20 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <p className="font-medium text-white">{day.day}</p>
                    <p className="text-sm font-bold text-green-400">
                      {Math.round(day.co2Saved * 10) / 10} kg CO₂
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-700 rounded-full h-3 overflow-hidden">
                      <div
                        className="bg-green-500 h-3 rounded-full"
                        style={{ width: `${(day.co2Saved / Math.max(...metrics.weeklyTrend.map(d => d.co2Saved))) * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-400">{day.ecoRoutes} routes</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Carbon Footprint */}
          <div className="glass rounded-xl shadow-lg p-6 border border-orange-500/30">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center">
              <Wind className="h-6 w-6 mr-2 text-orange-400" />
              Current Carbon Footprint
            </h2>
            
            <div className="text-center mb-6">
              <div className="text-5xl font-bold text-orange-400 mb-2">
                {metrics.carbonFootprint} kg
              </div>
              <p className="text-gray-400">Total CO₂ emissions</p>
            </div>

            <div className="space-y-4">
              <div className="glass border border-orange-500/20 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-gray-300">Eco Routes Impact</p>
                  <p className="text-sm font-bold text-green-400">
                    -{metrics.totalCO2Saved} kg
                  </p>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full"
                    style={{ width: `${(metrics.totalCO2Saved / metrics.carbonFootprint) * 100}%` }}
                  />
                </div>
              </div>

              <div className="glass border border-blue-500/20 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-gray-300">Energy Efficiency</p>
                  <p className="text-sm font-bold text-blue-400">
                    {metrics.energyEfficiency}%
                  </p>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${metrics.energyEfficiency}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Top Eco Areas */}
        <div className="glass rounded-xl shadow-lg p-6 border border-green-500/30 mb-8">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center">
            <Award className="h-6 w-6 mr-2 text-green-400" />
            Most Eco-Friendly Areas
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {metrics.topEcoAreas.map((area, index) => (
              <div
                key={index}
                className="glass border border-green-500/20 rounded-lg p-4 hover:border-green-500/50 transition-colors"
              >
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="font-medium text-white">Area {index + 1}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {area.lat.toFixed(3)}, {area.lng.toFixed(3)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-green-400">
                      {area.ecoPercentage.toFixed(1)}%
                    </p>
                    <p className="text-xs text-gray-400">eco routes</p>
                  </div>
                </div>
                <div className="mb-2">
                  <div className="flex justify-between text-xs text-gray-400 mb-1">
                    <span>{area.ecoRoutes} eco</span>
                    <span>{area.totalRoutes} total</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{ width: `${area.ecoPercentage}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Call to Action */}
        <div className="glass rounded-xl shadow-lg p-8 border border-green-500/30 text-center">
          <Recycle className="h-12 w-12 text-green-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-3">
            Make Every Trip Count
          </h2>
          <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
            Choose eco-friendly routes to reduce your carbon footprint. Every sustainable choice helps our city reach its environmental goals.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/route"
              className="px-6 py-3 btn-futuristic text-white rounded-lg transition-all duration-300"
            >
              Plan Eco Route
            </a>
            <a
              href="/analytics"
              className="px-6 py-3 glass border border-green-500/50 text-green-400 rounded-lg hover:bg-green-500/10 transition-all duration-300"
            >
              View Impact
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sustainability;


