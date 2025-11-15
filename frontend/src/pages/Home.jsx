import { Link } from 'react-router-dom';
import {
  AlertCircle,
  Route,
  Smile,
  Shield,
  MapPin,
  Activity,
  Sparkles,
  ArrowRight,
  Zap,
  Brain,
  Navigation,
  BarChart3
} from 'lucide-react';

const Home = () => {
  const features = [
    {
      icon: AlertCircle,
      title: 'Report Issues',
      description: 'Report infrastructure problems with image evidence and GPS location',
      link: '/report',
      gradient: 'from-red-500 to-orange-500',
      bgGradient: 'from-red-50 to-orange-50',
    },
    {
      icon: Route,
      title: 'Smart Routing',
      description: 'Plan routes optimized for driving, eco-friendliness, or quiet walking',
      link: '/route',
      gradient: 'from-blue-500 to-cyan-500',
      bgGradient: 'from-blue-50 to-cyan-50',
    },
    {
      icon: Smile,
      title: 'City Mood',
      description: 'View emotional sentiment analysis across different city areas',
      link: '/mood',
      gradient: 'from-green-500 to-emerald-500',
      bgGradient: 'from-green-50 to-emerald-50',
    },
    {
      icon: BarChart3,
      title: 'Analytics',
      description: 'Comprehensive city analytics: mood trends, accidents, and construction hotspots',
      link: '/analytics',
      gradient: 'from-cyan-500 to-blue-500',
      bgGradient: 'from-cyan-50 to-blue-50',
    },
    {
      icon: Shield,
      title: 'Admin Portal',
      description: 'Manage emergencies, work orders, and infrastructure issues',
      link: '/admin',
      gradient: 'from-purple-500 to-indigo-500',
      bgGradient: 'from-purple-50 to-indigo-50',
    },
  ];

  const capabilities = [
    {
      icon: MapPin,
      title: 'GPS-Powered Reporting',
      description: 'Automatic location capture with image evidence for accurate issue tracking',
      color: 'orange',
    },
    {
      icon: Brain,
      title: 'AI Analytics',
      description: 'Sentiment analysis, emergency summaries, and automated work order generation',
      color: 'indigo',
    },
    {
      icon: Navigation,
      title: 'Smart Routing',
      description: 'Multi-modal routing considering traffic, noise, and environmental factors',
      color: 'teal',
    },
  ];

  return (
    <div className="min-h-screen relative overflow-hidden">
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 z-10">
        {/* Hero Section */}
        <div className="text-center mb-20 animate-fade-in-up">
          <div className="flex items-center justify-center mb-8">
            <div className="relative">
              <div className="w-32 h-32 bg-gradient-to-br from-blue-500 via-purple-500 to-cyan-500 rounded-3xl flex items-center justify-center shadow-2xl hover:shadow-cyan-500/50 transition-all duration-500 hover:scale-110 hover:rotate-6 animate-scale-in glow-box">
                <Sparkles className="h-16 w-16 text-white animate-pulse" />
              </div>
              <div className="absolute -top-2 -right-2 w-8 h-8 bg-green-500 rounded-full border-4 border-slate-900 animate-heartbeat shadow-lg shadow-green-500/50"></div>
            </div>
          </div>

          <h1 className="text-6xl md:text-7xl font-bold mb-6 animate-fade-in-up stagger-1">
            <span className="text-white">Welcome to </span>
            <span className="neon-blue">NeuraCity</span>
          </h1>

          <p className="text-xl md:text-2xl text-gray-300 max-w-4xl mx-auto mb-8 leading-relaxed animate-fade-in-up stagger-2">
            An intelligent, human-centered smart city platform that merges{' '}
            <span className="font-semibold text-cyan-400 neon-cyan">AI analytics</span> with{' '}
            <span className="font-semibold text-purple-400">citizen reporting</span>{' '}
            for safer, smarter urban living
          </p>

          {/* System Status */}
          <div className="inline-flex items-center px-6 py-3 glass border border-green-500/50 text-green-400 rounded-full shadow-lg shadow-green-500/30 hover:shadow-green-500/50 transition-all duration-300 animate-fade-in-up stagger-3">
            <Activity className="h-5 w-5 mr-2 animate-pulse text-green-400" />
            <span className="font-medium">System Online & Ready</span>
            <Zap className="h-4 w-4 ml-2 text-green-400" />
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-8 mb-12 md:mb-20">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Link
                key={feature.title}
                to={feature.link}
                className={`group relative glass rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-500 p-8 border border-blue-500/30 overflow-hidden hover-lift animate-fade-in-up hover:border-cyan-500/50`}
                style={{ animationDelay: `${index * 100}ms` }}
              >
                {/* Holographic Background on Hover */}
                <div className={`absolute inset-0 holographic opacity-0 group-hover:opacity-100 transition-opacity duration-500`}></div>

                <div className="relative z-10">
                  {/* Icon with Gradient Glow */}
                  <div className={`w-16 h-16 bg-gradient-to-br ${feature.gradient} rounded-2xl flex items-center justify-center mb-5 shadow-lg group-hover:scale-110 group-hover:rotate-6 transition-all duration-500 glow-box`}>
                    <Icon className="h-8 w-8 text-white" />
                  </div>

                  <h2 className="text-2xl font-bold text-white mb-3 group-hover:text-cyan-400 transition-colors duration-300">
                    {feature.title}
                  </h2>

                  <p className="text-gray-300 leading-relaxed mb-4 group-hover:text-gray-200 transition-colors duration-300">
                    {feature.description}
                  </p>

                  <div className={`flex items-center font-semibold text-cyan-400 group-hover:text-cyan-300 group-hover:translate-x-2 transition-all duration-300`}>
                    Get Started
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </div>
                </div>

                {/* Decorative Corner Glow */}
                <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${feature.gradient} opacity-10 rounded-bl-full group-hover:opacity-20 transition-opacity duration-500`}></div>
              </Link>
            );
          })}
        </div>

        {/* Key Features Section */}
        <div className="glass rounded-2xl shadow-xl p-10 border border-blue-500/30 animate-fade-in-up stagger-4">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold text-white mb-3 neon-blue">
              Platform Capabilities
            </h2>
            <p className="text-gray-300">
              Powered by cutting-edge AI and real-time data processing
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 md:gap-8">
            {capabilities.map((capability, index) => {
              const Icon = capability.icon;
              const colorMap = {
                orange: 'from-orange-500 to-red-500',
                indigo: 'from-indigo-500 to-purple-500',
                teal: 'from-teal-500 to-cyan-500'
              };
              return (
                <div
                  key={capability.title}
                  className="text-center group hover:scale-105 transition-transform duration-300"
                  style={{ animationDelay: `${index * 100 + 400}ms` }}
                >
                  <div className={`w-16 h-16 bg-gradient-to-br ${colorMap[capability.color]} rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:-rotate-6 glow-box`}>
                    <Icon className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2 group-hover:text-cyan-400 transition-colors duration-300">
                    {capability.title}
                  </h3>
                  <p className="text-sm text-gray-300 leading-relaxed group-hover:text-gray-200 transition-colors duration-300">
                    {capability.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Connection Info */}
        <div className="mt-12 text-center">
          <div className="inline-flex items-center px-4 py-2 glass border border-blue-500/30 rounded-lg text-xs text-gray-300">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse shadow-lg shadow-green-500/50"></div>
            Backend API: {import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
