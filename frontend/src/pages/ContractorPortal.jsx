import { Construction, HardHat, Eye, ChevronDown, ChevronUp, Clock, CheckCircle, Filter } from 'lucide-react';
import { useEffect, useState } from 'react';
import { getWorkOrders } from '../lib/api';
import { formatDate, getIssueCategoryName } from '../lib/helpers';

// Helper function to get full image URL
const getImageUrl = (imageUrl) => {
  if (!imageUrl) return null;
  if (imageUrl.startsWith('http')) return imageUrl;
  const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
  const backendURL = baseURL.replace('/api/v1', '');
  return `${backendURL}/${imageUrl}`;
};

const ContractorPortal = () => {
  const [workOrders, setWorkOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [expandedOrders, setExpandedOrders] = useState(new Set());
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    fetchWorkOrders();
  }, []);

  const fetchWorkOrders = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getWorkOrders();
      setWorkOrders(data || []);
    } catch (err) {
      setError(err.message || 'Failed to load work orders');
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (orderId) => {
    const newExpanded = new Set(expandedOrders);
    if (newExpanded.has(orderId)) {
      newExpanded.delete(orderId);
    } else {
      newExpanded.add(orderId);
    }
    setExpandedOrders(newExpanded);
  };

  const filteredOrders = statusFilter === 'all'
    ? workOrders
    : workOrders.filter(order => order.status === statusFilter);

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending_review':
        return { bg: 'bg-yellow-500/20', text: 'text-yellow-400', border: 'border-yellow-500/50' };
      case 'approved':
        return { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500/50' };
      case 'in_progress':
        return { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500/50' };
      case 'completed':
        return { bg: 'bg-emerald-500/20', text: 'text-emerald-400', border: 'border-emerald-500/50' };
      default:
        return { bg: 'bg-gray-500/20', text: 'text-gray-400', border: 'border-gray-500/50' };
    }
  };

  return (
    <div className="min-h-screen py-4 md:py-8 relative z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header with Urban Theme */}
        <div className="mb-4 md:mb-8 relative">
          <div className="absolute inset-0 urban-pattern opacity-20 pointer-events-none rounded-lg"></div>
          <div className="relative">
            <div className="flex items-center mb-2">
              <Construction className="h-8 w-8 md:h-10 md:w-10 text-construction-orange mr-3 animate-pulse" style={{ color: 'var(--color-construction-orange)' }} />
              <h1 className="text-2xl md:text-3xl lg:text-4xl font-bold text-white neon-blue">
                Contractor Portal
              </h1>
            </div>
            <p className="text-sm md:text-base lg:text-lg text-gray-300 ml-11 md:ml-13">
              Manage infrastructure repair work orders and view issue details
            </p>
          </div>
        </div>

        {/* Filter Bar */}
        <div className="infrastructure-card rounded-lg shadow p-4 mb-6">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center text-white">
              <Filter className="h-5 w-5 mr-2 text-construction-orange" style={{ color: 'var(--color-construction-orange)' }} />
              <span className="font-semibold text-base">Filter by Status:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {['all', 'pending_review', 'approved', 'in_progress', 'completed'].map((status) => (
                <button
                  key={status}
                  onClick={() => setStatusFilter(status)}
                  className={`px-4 py-2 rounded-lg font-medium text-sm transition-all duration-300 ${
                    statusFilter === status
                      ? 'btn-construction'
                      : 'glass border border-gray-500/30 text-gray-300 hover:border-construction-orange hover:text-construction-orange'
                  }`}
                  style={statusFilter === status ? {} : { borderColor: 'var(--color-concrete-gray)' }}
                >
                  {status === 'all' ? 'All Orders' : status.replace('_', ' ').toUpperCase()}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="infrastructure-card rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400 font-medium">Total Orders</p>
                <p className="text-2xl md:text-3xl font-bold text-white mt-1">{workOrders.length}</p>
              </div>
              <HardHat className="h-10 w-10 text-construction-orange" style={{ color: 'var(--color-construction-orange)' }} />
            </div>
          </div>
          <div className="infrastructure-card rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400 font-medium">Pending Review</p>
                <p className="text-2xl md:text-3xl font-bold text-yellow-400 mt-1">
                  {workOrders.filter(o => o.status === 'pending_review').length}
                </p>
              </div>
              <Clock className="h-10 w-10 text-yellow-400" />
            </div>
          </div>
          <div className="infrastructure-card rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400 font-medium">In Progress</p>
                <p className="text-2xl md:text-3xl font-bold text-blue-400 mt-1">
                  {workOrders.filter(o => o.status === 'in_progress').length}
                </p>
              </div>
              <Construction className="h-10 w-10 text-blue-400" />
            </div>
          </div>
          <div className="infrastructure-card rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400 font-medium">Completed</p>
                <p className="text-2xl md:text-3xl font-bold text-emerald-400 mt-1">
                  {workOrders.filter(o => o.status === 'completed').length}
                </p>
              </div>
              <CheckCircle className="h-10 w-10 text-emerald-400" />
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 glass border border-red-500/30 rounded-lg p-4">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {/* Work Orders List */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Construction className="h-12 w-12 text-construction-orange animate-spin" style={{ color: 'var(--color-construction-orange)' }} />
          </div>
        ) : filteredOrders.length === 0 ? (
          <div className="infrastructure-card rounded-lg shadow p-12 text-center">
            <Construction className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <p className="text-lg text-gray-300 font-medium">No work orders found</p>
            <p className="text-sm text-gray-400 mt-2">
              {statusFilter !== 'all' ? 'Try changing the filter' : 'Work orders will appear here when created'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredOrders.map((order) => {
              const isExpanded = expandedOrders.has(order.id);
              const statusStyle = getStatusColor(order.status);
              const categoryName = order.issue
                ? getIssueCategoryName(order.issue.issue_type, order.issue.description)
                : 'Unknown Issue';

              return (
                <div key={order.id} className="infrastructure-card rounded-lg shadow overflow-hidden">
                  {/* Card Header */}
                  <div className="p-4 md:p-6">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h3 className="text-lg md:text-xl font-bold text-white mb-1">
                          {categoryName}
                        </h3>
                        <p className="text-sm text-gray-400">
                          Created {formatDate(order.created_at)}
                        </p>
                        {order.issue?.location_name && (
                          <p className="text-sm text-cyan-400 mt-1 flex items-center">
                            <span className="mr-1">📍</span>
                            {order.issue.location_name}
                          </p>
                        )}
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-bold border ${statusStyle.bg} ${statusStyle.text} ${statusStyle.border} whitespace-nowrap ml-2`}>
                        {order.status.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>

                    {/* Quick Info */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
                      {order.contractor_name && (
                        <div className="glass border border-purple-500/30 rounded-lg p-3">
                          <p className="text-xs text-purple-400 font-semibold mb-1">ASSIGNED TO</p>
                          <p className="text-sm font-bold text-white">{order.contractor_name}</p>
                          {order.contractor_specialty && (
                            <p className="text-xs text-gray-400 capitalize mt-1">
                              {order.contractor_specialty.replace('_', ' ')}
                            </p>
                          )}
                        </div>
                      )}
                      {order.issue && (
                        <div className="glass border border-blue-500/30 rounded-lg p-3">
                          <p className="text-xs text-cyan-400 font-semibold mb-1">COORDINATES</p>
                          <p className="text-sm text-white font-mono">
                            {order.issue.lat.toFixed(4)}, {order.issue.lng.toFixed(4)}
                          </p>
                        </div>
                      )}
                    </div>

                    {/* View More Button */}
                    <button
                      onClick={() => toggleExpand(order.id)}
                      className="w-full flex items-center justify-center px-4 py-3 glass border border-construction-orange rounded-lg text-base font-semibold text-white hover:bg-construction-orange/20 transition-all duration-300"
                      style={{ borderColor: 'var(--color-construction-orange)' }}
                    >
                      {isExpanded ? (
                        <>
                          <ChevronUp className="h-5 w-5 mr-2" />
                          View Less
                        </>
                      ) : (
                        <>
                          <ChevronDown className="h-5 w-5 mr-2" />
                          View More Details
                        </>
                      )}
                    </button>
                  </div>

                  {/* Expandable Content */}
                  {isExpanded && (
                    <div className="border-t border-construction-orange/30 p-4 md:p-6 bg-black/20 animate-fade-in" style={{ borderTopColor: 'var(--color-construction-orange)' }}>
                      {/* Full Issue Description */}
                      {order.issue?.description && (
                        <div className="mb-4 p-4 glass border border-blue-500/30 rounded-lg">
                          <p className="text-xs font-bold text-cyan-400 mb-2 uppercase tracking-wide">
                            Issue Description
                          </p>
                          <p className="text-base text-white leading-relaxed whitespace-pre-wrap">
                            {order.issue.description}
                          </p>
                        </div>
                      )}

                      {/* Issue Image */}
                      {order.issue?.image_url && (
                        <div className="mb-4">
                          <button
                            onClick={() => setSelectedImage(getImageUrl(order.issue.image_url))}
                            className="flex items-center text-cyan-400 hover:text-cyan-300 font-bold text-base transition-colors"
                          >
                            <Eye className="h-5 w-5 mr-2" />
                            View Issue Evidence Photo
                          </button>
                        </div>
                      )}

                      {/* Material Suggestions */}
                      {order.material_suggestion && (
                        <div className="mb-4 p-4 glass border border-safety-yellow/30 rounded-lg" style={{ borderColor: 'var(--color-safety-yellow)' }}>
                          <p className="text-xs font-bold mb-2 uppercase tracking-wide" style={{ color: 'var(--color-safety-yellow)' }}>
                            🤖 AI-Generated Repair Plan & Materials
                          </p>
                          <div className="text-base text-white leading-relaxed whitespace-pre-wrap">
                            {order.material_suggestion}
                          </div>
                        </div>
                      )}

                      {/* Full Contractor Info */}
                      {order.contractor_name && (
                        <div className="p-4 glass border border-purple-500/30 rounded-lg">
                          <p className="text-xs font-bold text-purple-400 mb-3 uppercase tracking-wide">
                            Contractor Information
                          </p>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                            <div>
                              <p className="text-gray-400">Name:</p>
                              <p className="text-white font-bold text-base">{order.contractor_name}</p>
                            </div>
                            {order.contractor_specialty && (
                              <div>
                                <p className="text-gray-400">Specialty:</p>
                                <p className="text-white font-medium capitalize">
                                  {order.contractor_specialty.replace('_', ' ')}
                                </p>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Image Modal */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div className="relative max-w-5xl max-h-full">
            <button
              onClick={() => setSelectedImage(null)}
              className="absolute -top-12 right-0 text-white hover:text-gray-300 text-2xl font-bold"
            >
              ✕ Close
            </button>
            <img
              src={selectedImage}
              alt="Issue Evidence"
              className="max-w-full max-h-[90vh] object-contain rounded-lg shadow-2xl border-4 border-construction-orange"
              style={{ borderColor: 'var(--color-construction-orange)' }}
              onClick={(e) => e.stopPropagation()}
            />
            <p className="text-white text-center mt-4 text-sm">Click outside image to close</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContractorPortal;
