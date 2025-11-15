import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, AlertCircle, Route, Smile, Shield, Menu, X, Sparkles } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { path: '/', label: 'Home', icon: Home },
    { path: '/report', label: 'Report Issue', icon: AlertCircle },
    { path: '/route', label: 'Plan Route', icon: Route },
    { path: '/mood', label: 'Mood Map', icon: Smile },
    { path: '/admin', label: 'Admin', icon: Shield },
  ];

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  return (
    <nav className="sticky top-0 z-50 glass-dark border-b border-blue-500/30 shadow-lg animate-fade-in-down">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center group" onClick={() => setMobileMenuOpen(false)}>
            <div className="flex items-center">
              <div className="relative w-12 h-12 bg-gradient-to-br from-blue-500 via-purple-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-2xl transition-all duration-300 group-hover:scale-110 glow-box">
                <Sparkles className="h-6 w-6 text-white animate-pulse" />
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-blue-400/50 to-purple-400/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </div>
              <span className="ml-3 text-xl font-bold neon-blue">
                NeuraCity
              </span>
            </div>
          </Link>

          {/* Navigation Links - Desktop */}
          <div className="hidden md:flex items-center space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`relative flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                    isActive
                      ? 'text-cyan-400 neon-cyan bg-blue-500/20 border border-cyan-500/50'
                      : 'text-gray-300 hover:text-cyan-400 hover:bg-blue-500/10 border border-transparent'
                  }`}
                >
                  <Icon className={`h-4 w-4 mr-2 ${isActive ? 'text-cyan-400' : ''}`} />
                  {item.label}
                  {isActive && (
                    <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500 via-cyan-500 to-purple-500 rounded-full animate-scale-in shadow-lg shadow-cyan-500/50"></span>
                  )}
                </Link>
              );
            })}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={toggleMobileMenu}
              className="text-gray-300 hover:text-cyan-400 p-3 rounded-lg hover:bg-blue-500/10 transition-colors min-w-[44px] min-h-[44px] flex items-center justify-center"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation - Animated Dropdown */}
      <div
        className={`md:hidden border-t border-blue-500/30 glass-dark transition-all duration-300 ease-in-out ${
          mobileMenuOpen
            ? 'max-h-96 opacity-100'
            : 'max-h-0 opacity-0 overflow-hidden'
        }`}
      >
        <div className="px-2 pt-2 pb-3 space-y-1">
          {navItems.map((item, index) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center px-4 py-4 rounded-lg text-base font-medium transition-all duration-300 min-h-[44px] ${
                  isActive
                    ? 'bg-blue-500/20 text-cyan-400 border border-cyan-500/50 shadow-sm'
                    : 'text-gray-300 hover:bg-blue-500/10 hover:text-cyan-400'
                }`}
                style={{
                  animationDelay: `${index * 50}ms`,
                  animation: mobileMenuOpen ? 'fadeInUp 0.3s ease-out forwards' : 'none'
                }}
              >
                <Icon className="h-5 w-5 mr-3" />
                {item.label}
                {isActive && (
                  <span className="ml-auto w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></span>
                )}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
