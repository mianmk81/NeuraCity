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
  Navigation
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
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-secondary-50 to-indigo-50 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-secondary-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-indigo-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Hero Section */}
        <div className="text-center mb-20 animate-fade-in-up">
          <div className="flex items-center justify-center mb-8">
            <div className="relative">
              <div className="w-24 h-24 bg-gradient-primary rounded-3xl flex items-center justify-center shadow-2xl hover:shadow-3xl transition-all duration-500 hover:scale-110 hover:rotate-6 animate-scale-in">
                <Sparkles className="h-12 w-12 text-white animate-pulse" />
              </div>
              <div className="absolute -top-1 -right-1 w-6 h-6 bg-green-500 rounded-full border-4 border-white animate-heartbeat"></div>
            </div>
          </div>

          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 animate-fade-in-up stagger-1">
            Welcome to{' '}
            <span className="text-gradient">NeuraCity</span>
          </h1>

          <p className="text-xl md:text-2xl text-gray-600 max-w-4xl mx-auto mb-8 leading-relaxed animate-fade-in-up stagger-2">
            An intelligent, human-centered smart city platform that merges{' '}
            <span className="font-semibold text-primary-600">AI analytics</span> with{' '}
            <span className="font-semibold text-secondary-600">citizen reporting</span>{' '}
            for safer, smarter urban living
          </p>

          {/* System Status */}
          <div className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-emerald-50 to-green-50 border border-emerald-200 text-emerald-800 rounded-full shadow-md hover:shadow-lg transition-all duration-300 animate-fade-in-up stagger-3">
            <Activity className="h-5 w-5 mr-2 animate-pulse" />
            <span className="font-medium">System Online & Ready</span>
            <Zap className="h-4 w-4 ml-2 text-emerald-600" />
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-20">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Link
                key={feature.title}
                to={feature.link}
                className={`group relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-500 p-8 border border-gray-100 overflow-hidden hover-lift animate-fade-in-up`}
                style={{ animationDelay: `${index * 100}ms` }}
              >
                {/* Gradient Background on Hover */}
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.bgGradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`}></div>

                <div className="relative z-10">
                  {/* Icon with Gradient */}
                  <div className={`w-16 h-16 bg-gradient-to-br ${feature.gradient} rounded-2xl flex items-center justify-center mb-5 shadow-lg group-hover:scale-110 group-hover:rotate-6 transition-all duration-500`}>
                    <Icon className="h-8 w-8 text-white" />
                  </div>

                  <h2 className="text-2xl font-bold text-gray-900 mb-3 group-hover:text-gray-800">
                    {feature.title}
                  </h2>

                  <p className="text-gray-600 leading-relaxed mb-4 group-hover:text-gray-700">
                    {feature.description}
                  </p>

                  <div className={`flex items-center font-semibold bg-gradient-to-r ${feature.gradient} bg-clip-text text-transparent group-hover:translate-x-2 transition-transform duration-300`}>
                    Get Started
                    <ArrowRight className="ml-2 h-5 w-5 text-primary-600" />
                  </div>
                </div>

                {/* Decorative Corner */}
                <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${feature.gradient} opacity-5 rounded-bl-full`}></div>
              </Link>
            );
          })}
        </div>

        {/* Key Features Section */}
        <div className="bg-white rounded-2xl shadow-xl p-10 border border-gray-100 animate-fade-in-up stagger-4">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold text-gray-900 mb-3">
              Platform Capabilities
            </h2>
            <p className="text-gray-600">
              Powered by cutting-edge AI and real-time data processing
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {capabilities.map((capability, index) => {
              const Icon = capability.icon;
              return (
                <div
                  key={capability.title}
                  className="text-center group hover:scale-105 transition-transform duration-300"
                  style={{ animationDelay: `${index * 100 + 400}ms` }}
                >
                  <div className={`w-16 h-16 bg-${capability.color}-100 text-${capability.color}-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-md group-hover:shadow-lg transition-all duration-300 group-hover:-rotate-6`}>
                    <Icon className="h-8 w-8" />
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 mb-2">
                    {capability.title}
                  </h3>
                  <p className="text-sm text-gray-600 leading-relaxed">
                    {capability.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Connection Info */}
        <div className="mt-12 text-center">
          <div className="inline-flex items-center px-4 py-2 bg-gray-100 rounded-lg text-xs text-gray-500">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
            Backend API: {import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
