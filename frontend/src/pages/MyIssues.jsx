import { AlertTriangle, CheckCircle, Clock, Eye, ChevronDown, ChevronUp, Filter, TrendingUp } from 'lucide-react';
import { useEffect, useState } from 'react';
import { getIssues } from '../lib/api';
import { formatDate, getIssueCategoryName, getPriorityColor } from '../lib/helpers';

// Helper function to get full image URL
const getImageUrl = (imageUrl) => {
  if (!imageUrl) return null;
  if (imageUrl.startsWith('http')) return imageUrl;
  const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
  const backendURL = baseURL.replace('/api/v1', '');
  return `${backendURL}/${imageUrl}`;
};

const MyIssues = () => {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [expandedIssues, setExpandedIssues] = useState(new Set());
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');

  useEffect(() => {
    fetchIssues();
  }, []);

  const fetchIssues = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getIssues({ limit: 1000 });
      setIssues(data || []);
    } catch (err) {
      setError(err.message || 'Failed to load issues');
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (issueId) => {
    const newExpanded = new Set(expandedIssues);
    if (newExpanded.has(issueId)) {
      newExpanded.delete(issueId);
    } else {
      newExpanded.add(issueId);
    }
    setExpandedIssues(newExpanded);
  };

  let filteredIssues = issues;
  if (statusFilter !== 'all') {
    filteredIssues = filteredIssues.filter(issue => issue.status === statusFilter);
  }
  if (typeFilter !== 'all') {
    filteredIssues = filteredIssues.filter(issue => issue.issue_type === typeFilter);
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'open':
        return <Clock className="h-5 w-5" />;
      case 'in_progress':
        return <TrendingUp className="h-5 w-5" />;
      case 'resolved':
        return <CheckCircle className="h-5 w-5" />;
      default:
        return <AlertTriangle className="h-5 w-5" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'open':
        return { bg: 'bg-yellow-500/20', text: 'text-yellow-400', border: 'border-yellow-500/50' };
      case 'in_progress':
        return { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500/50' };
      case 'resolved':
        return { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500/50' };
      case 'closed':
        return { bg: 'bg-gray-500/20', text: 'text-gray-400', border: 'border-gray-500/50' };
      default:
        return { bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500/50' };
    }
  };

  const getActionBadge = (actionType) => {
    switch (actionType) {
      case 'emergency':
        return { label: 'EMERGENCY QUEUE', color: 'bg-red-500/20 text-red-400 border-red-500/50' };
      case 'work_order':
        return { label: 'WORK ORDER CREATED', color: 'bg-construction-orange/20 border-construction-orange/50' };
      case 'monitor':
        return { label: 'MONITORING', color: 'bg-blue-500/20 text-blue-400 border-blue-500/50' };
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen py-4 md:py-8 relative z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-4 md:mb-8">
          <div className="flex items-center mb-2">
            <AlertTriangle className="h-8 w-8 md:h-10 md:w-10 text-cyan-400 mr-3" />
            <h1 className="text-2xl md:text-3xl lg:text-4xl font-bold text-white neon-blue">
              My Reported Issues
            </h1>
          </div>
          <p className="text-sm md:text-base lg:text-lg text-gray-300 ml-11 md:ml-13">
            Track the status and progress of your issue reports
          </p>
        </div>

        {/* Filter Bar */}
        <div className="glass rounded-lg shadow p-4 mb-6 border border-blue-500/30">
          <div className="space-y-4">
            {/* Status Filter */}
            <div>
              <div className="flex items-center text-white mb-2">
                <Filter className="h-5 w-5 mr-2 text-cyan-400" />
                <span className="font-semibold text-base">Filter by Status:</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {['all', 'open', 'in_progress', 'resolved', 'closed'].map((status) => (
                  <button
                    key={status}
                    onClick={() => setStatusFilter(status)}
                    className={`px-4 py-2 rounded-lg font-medium text-sm transition-all duration-300 ${
                      statusFilter === status
                        ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-lg'
                        : 'glass border border-gray-500/30 text-gray-300 hover:border-cyan-500 hover:text-cyan-400'
                    }`}
                  >
                    {status === 'all' ? 'All Issues' : status.replace('_', ' ').toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            {/* Type Filter */}
            <div>
              <div className="flex items-center text-white mb-2">
                <Filter className="h-5 w-5 mr-2 text-cyan-400" />
                <span className="font-semibold text-base">Filter by Type:</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {['all', 'accident', 'pothole', 'traffic_light', 'other'].map((type) => (
                  <button
                    key={type}
                    onClick={() => setTypeFilter(type)}
                    className={`px-4 py-2 rounded-lg font-medium text-sm transition-all duration-300 ${
                      typeFilter === type
                        ? 'bg-gradient-to-r from-purple-500 to-indigo-500 text-white shadow-lg'
                        : 'glass border border-gray-500/30 text-gray-300 hover:border-purple-500 hover:text-purple-400'
                    }`}
                  >
                    {type === 'all' ? 'All Types' : type.replace('_', ' ').toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 md:gap-4 mb-6">
          <div className="glass rounded-lg shadow p-3 md:p-4 border border-blue-500/30">
            <p className="text-xs md:text-sm text-gray-400 font-medium">Total Reports</p>
            <p className="text-xl md:text-3xl font-bold text-white mt-1">{issues.length}</p>
          </div>
          <div className="glass rounded-lg shadow p-3 md:p-4 border border-yellow-500/30">
            <p className="text-xs md:text-sm text-gray-400 font-medium">Open</p>
            <p className="text-xl md:text-3xl font-bold text-yellow-400 mt-1">
              {issues.filter(i => i.status === 'open').length}
            </p>
          </div>
          <div className="glass rounded-lg shadow p-3 md:p-4 border border-blue-500/30">
            <p className="text-xs md:text-sm text-gray-400 font-medium">In Progress</p>
            <p className="text-xl md:text-3xl font-bold text-blue-400 mt-1">
              {issues.filter(i => i.status === 'in_progress').length}
            </p>
          </div>
          <div className="glass rounded-lg shadow p-3 md:p-4 border border-green-500/30">
            <p className="text-xs md:text-sm text-gray-400 font-medium">Resolved</p>
            <p className="text-xl md:text-3xl font-bold text-green-400 mt-1">
              {issues.filter(i => i.status === 'resolved').length}
            </p>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 glass border border-red-500/30 rounded-lg p-4">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {/* Issues List */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Clock className="h-12 w-12 text-cyan-400 animate-spin" />
          </div>
        ) : filteredIssues.length === 0 ? (
          <div className="glass rounded-lg shadow p-12 text-center border border-blue-500/30">
            <AlertTriangle className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <p className="text-lg text-gray-300 font-medium">No issues found</p>
            <p className="text-sm text-gray-400 mt-2">
              {statusFilter !== 'all' || typeFilter !== 'all'
                ? 'Try changing the filters'
                : 'Your reported issues will appear here'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredIssues.map((issue) => {
              const isExpanded = expandedIssues.has(issue.id);
              const statusStyle = getStatusColor(issue.status);
              const categoryName = getIssueCategoryName(issue.issue_type, issue.description);
              const actionBadge = getActionBadge(issue.action_type);
              const priorityColor = getPriorityColor(issue.priority);

              return (
                <div key={issue.id} className="glass rounded-lg shadow overflow-hidden border border-blue-500/30 hover:border-cyan-500/50 transition-all duration-300">
                  {/* Timeline Indicator (Left Border) */}
                  <div
                    className="absolute left-0 top-0 bottom-0 w-1"
                    style={{ backgroundColor: priorityColor }}
                  ></div>

                  {/* Card Header */}
                  <div className="p-4 md:p-6 pl-6 md:pl-8">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="text-lg md:text-xl font-bold text-white">
                            {categoryName}
                          </h3>
                        </div>
                        <p className="text-sm text-gray-400">
                          Reported {formatDate(issue.created_at)}
                        </p>
                        {issue.location_name && (
                          <p className="text-sm text-cyan-400 mt-1 flex items-center">
                            <span className="mr-1">📍</span>
                            {issue.location_name}
                          </p>
                        )}
                      </div>
                      <div className="flex flex-col items-end gap-2 ml-2">
                        <span className={`px-3 py-1 rounded-full text-xs font-bold border flex items-center gap-1 ${statusStyle.bg} ${statusStyle.text} ${statusStyle.border} whitespace-nowrap`}>
                          {getStatusIcon(issue.status)}
                          {issue.status.replace('_', ' ').toUpperCase()}
                        </span>
                        {issue.priority && (
                          <span
                            className="px-3 py-1 rounded-full text-xs font-bold border whitespace-nowrap"
                            style={{
                              backgroundColor: `${priorityColor}20`,
                              color: priorityColor,
                              borderColor: `${priorityColor}50`,
                            }}
                          >
                            {issue.priority.toUpperCase()}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Action Badge */}
                    {actionBadge && (
                      <div className={`inline-flex items-center px-3 py-1 rounded-lg text-xs font-bold border mb-3 ${actionBadge.color}`}
                        style={issue.action_type === 'work_order' ? { color: 'var(--color-construction-orange)', borderColor: 'var(--color-construction-orange)' } : {}}>
                        {actionBadge.label}
                      </div>
                    )}

                    {/* Quick Metrics */}
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
                      <div className="glass border border-blue-500/30 rounded-lg p-3">
                        <p className="text-xs text-cyan-400 font-semibold mb-1">SEVERITY</p>
                        <p className="text-sm font-bold text-white">
                          {issue.severity ? `${(issue.severity * 100).toFixed(0)}%` : 'N/A'}
                        </p>
                      </div>
                      <div className="glass border border-blue-500/30 rounded-lg p-3">
                        <p className="text-xs text-cyan-400 font-semibold mb-1">URGENCY</p>
                        <p className="text-sm font-bold text-white">
                          {issue.urgency ? `${(issue.urgency * 100).toFixed(0)}%` : 'N/A'}
                        </p>
                      </div>
                      <div className="glass border border-blue-500/30 rounded-lg p-3">
                        <p className="text-xs text-cyan-400 font-semibold mb-1">COORDINATES</p>
                        <p className="text-xs text-white font-mono">
                          {issue.lat.toFixed(3)}, {issue.lng.toFixed(3)}
                        </p>
                      </div>
                    </div>

                    {/* View More Button */}
                    <button
                      onClick={() => toggleExpand(issue.id)}
                      className="w-full flex items-center justify-center px-4 py-3 glass border border-cyan-500 rounded-lg text-base font-semibold text-white hover:bg-cyan-500/20 transition-all duration-300"
                    >
                      {isExpanded ? (
                        <>
                          <ChevronUp className="h-5 w-5 mr-2" />
                          View Less
                        </>
                      ) : (
                        <>
                          <ChevronDown className="h-5 w-5 mr-2" />
                          View Full Details
                        </>
                      )}
                    </button>
                  </div>

                  {/* Expandable Content */}
                  {isExpanded && (
                    <div className="border-t border-cyan-500/30 p-4 md:p-6 pl-6 md:pl-8 bg-black/20 animate-fade-in">
                      {/* Full Description */}
                      {issue.description && (
                        <div className="mb-4 p-4 glass border border-blue-500/30 rounded-lg">
                          <p className="text-xs font-bold text-cyan-400 mb-2 uppercase tracking-wide">
                            Full Description
                          </p>
                          <p className="text-base text-white leading-relaxed whitespace-pre-wrap">
                            {issue.description}
                          </p>
                        </div>
                      )}

                      {/* Issue Image */}
                      {issue.image_url && (
                        <div className="mb-4">
                          <button
                            onClick={() => setSelectedImage(getImageUrl(issue.image_url))}
                            className="flex items-center text-cyan-400 hover:text-cyan-300 font-bold text-base transition-colors"
                          >
                            <Eye className="h-5 w-5 mr-2" />
                            View Evidence Photo
                          </button>
                        </div>
                      )}

                      {/* Lifecycle Timeline */}
                      <div className="p-4 glass border border-purple-500/30 rounded-lg">
                        <p className="text-xs font-bold text-purple-400 mb-3 uppercase tracking-wide">
                          Issue Lifecycle
                        </p>
                        <div className="space-y-2">
                          <div className="flex items-center text-sm">
                            <div className={`w-3 h-3 rounded-full mr-3 ${issue.status === 'open' || issue.status === 'in_progress' || issue.status === 'resolved' ? 'bg-green-400' : 'bg-gray-600'}`}></div>
                            <span className="text-white font-medium">Reported</span>
                            <span className="ml-auto text-gray-400">{formatDate(issue.created_at)}</span>
                          </div>
                          <div className="flex items-center text-sm">
                            <div className={`w-3 h-3 rounded-full mr-3 ${issue.status === 'in_progress' || issue.status === 'resolved' ? 'bg-green-400' : issue.status === 'open' ? 'bg-yellow-400' : 'bg-gray-600'}`}></div>
                            <span className="text-white font-medium">Under Review / In Progress</span>
                            <span className="ml-auto text-gray-400">
                              {issue.status === 'in_progress' || issue.status === 'resolved' ? 'Active' : 'Pending'}
                            </span>
                          </div>
                          <div className="flex items-center text-sm">
                            <div className={`w-3 h-3 rounded-full mr-3 ${issue.status === 'resolved' ? 'bg-green-400' : 'bg-gray-600'}`}></div>
                            <span className="text-white font-medium">Resolved</span>
                            <span className="ml-auto text-gray-400">
                              {issue.status === 'resolved' ? 'Completed' : 'Waiting'}
                            </span>
                          </div>
                        </div>
                      </div>
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
              className="max-w-full max-h-[90vh] object-contain rounded-lg shadow-2xl border-4 border-cyan-500"
              onClick={(e) => e.stopPropagation()}
            />
            <p className="text-white text-center mt-4 text-sm">Click outside image to close</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default MyIssues;
