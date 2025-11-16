import { useState, useEffect } from 'react';
import { CheckCircle, Clock, Wrench, Package, User, Eye, ChevronDown, ChevronUp } from 'lucide-react';
import { formatDate, getIssueCategoryName } from '../lib/helpers';
import { getContractors, assignContractor } from '../lib/api';

const WorkOrderCard = ({ workOrder, onApprove, onUpdate }) => {
  const [isApproving, setIsApproving] = useState(false);
  const [contractors, setContractors] = useState([]);
  const [selectedContractor, setSelectedContractor] = useState(workOrder.contractor_id || '');
  const [isAssigning, setIsAssigning] = useState(false);
  const [showImage, setShowImage] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const isApproved = workOrder.status === 'approved';
  const isPending = workOrder.status === 'pending_review';
  const hasContractor = !!workOrder.contractor_id;

  // Fetch contractors on mount
  useEffect(() => {
    const fetchContractors = async () => {
      try {
        // Extract specialty from material_suggestion if available
        let specialty = null;
        if (workOrder.material_suggestion && workOrder.material_suggestion.includes('pothole')) {
          specialty = 'pothole_repair';
        }
        const data = await getContractors(specialty);
        setContractors(data || []);
      } catch (error) {
        console.error('Failed to fetch contractors:', error);
      }
    };
    if (!hasContractor) {
      fetchContractors();
    }
  }, [workOrder, hasContractor]);

  const handleAssignContractor = async () => {
    if (!selectedContractor) return;
    setIsAssigning(true);
    try {
      const updated = await assignContractor(workOrder.id, selectedContractor);
      if (onUpdate) {
        onUpdate(updated);
      }
    } catch (error) {
      console.error('Failed to assign contractor:', error);
    } finally {
      setIsAssigning(false);
    }
  };

  const handleApprove = async () => {
    setIsApproving(true);
    try {
      await onApprove(workOrder.id);
    } catch (error) {
      console.error('Failed to approve work order:', error);
    } finally {
      setIsApproving(false);
    }
  };

  const getImageUrl = (imageUrl) => {
    if (!imageUrl) return null;
    if (imageUrl.startsWith('http')) return imageUrl;
    const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
    const backendURL = baseURL.replace('/api/v1', '');
    return `${backendURL}/${imageUrl}`;
  };

  // Get category name for title
  const categoryName = workOrder.issue
    ? getIssueCategoryName(workOrder.issue.issue_type, workOrder.issue.description)
    : 'Unknown Issue';

  return (
    <div className="infrastructure-card rounded-lg shadow overflow-hidden">
      <div className="p-5">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-lg md:text-xl font-bold text-white mb-1">
              {categoryName}
            </h3>
            <p className="text-sm text-gray-400">
              {formatDate(workOrder.created_at)}
            </p>
            {workOrder.issue?.location_name && (
              <p className="text-sm text-cyan-400 mt-1 flex items-center">
                <span className="mr-1">📍</span>
                {workOrder.issue.location_name}
              </p>
            )}
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-bold border whitespace-nowrap ml-2 ${
            isApproved ? 'bg-green-500/20 text-green-400 border-green-500/50' :
            isPending ? 'badge-safety' :
            'bg-gray-500/20 text-gray-400 border-gray-500/50'
          }`} style={isPending ? { backgroundColor: 'var(--color-safety-yellow)20', color: '#1a1a1a', borderColor: 'var(--color-safety-yellow)' } : {}}>
            {workOrder.status.replace('_', ' ').toUpperCase()}
          </span>
        </div>

      {/* Quick Info - Always Visible */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
        {workOrder.issue && (
          <div className="glass border border-blue-500/30 rounded-lg p-3">
            <p className="text-xs text-cyan-400 font-semibold mb-1">LOCATION</p>
            <p className="text-sm text-white font-mono">
              {workOrder.issue.lat.toFixed(4)}, {workOrder.issue.lng.toFixed(4)}
            </p>
          </div>
        )}
        {hasContractor && (
          <div className="glass border border-purple-500/30 rounded-lg p-3">
            <p className="text-xs text-purple-400 font-semibold mb-1">CONTRACTOR</p>
            <p className="text-sm font-bold text-white">{workOrder.contractor_name || 'Assigned'}</p>
          </div>
        )}
      </div>

      {/* View More Button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-center px-4 py-3 glass border border-construction-orange rounded-lg text-base font-semibold text-white hover:bg-construction-orange/20 transition-all duration-300 mb-4"
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
            View Full Details
          </>
        )}
      </button>

      {/* Expandable Detailed Content */}
      {isExpanded && (
        <div className="border-t border-construction-orange/30 pt-4 mb-4 animate-fade-in" style={{ borderTopColor: 'var(--color-construction-orange)' }}>
          {/* Full Issue Description */}
          {workOrder.issue?.description && (
            <div className="mb-4 p-4 glass border border-blue-500/30 rounded-lg">
              <p className="text-xs font-bold text-cyan-400 mb-2 uppercase tracking-wide">
                Issue Description
              </p>
              <p className="text-base text-white leading-relaxed whitespace-pre-wrap">
                {workOrder.issue.description}
              </p>
            </div>
          )}

          {/* Issue Image */}
          {workOrder.issue?.image_url && (
            <div className="mb-4">
              <button
                onClick={() => setShowImage(true)}
                className="flex items-center text-cyan-400 hover:text-cyan-300 font-bold text-base transition-colors"
              >
                <Eye className="h-5 w-5 mr-2" />
                View Issue Evidence Photo
              </button>
            </div>
          )}

          {/* Material Suggestion - Full Details */}
          {workOrder.material_suggestion && (
            <div className="mb-4 p-4 glass border border-safety-yellow/30 rounded-lg" style={{ borderColor: 'var(--color-safety-yellow)' }}>
              <div className="flex items-start">
                <Package className="h-5 w-5 mr-2 mt-0.5 flex-shrink-0" style={{ color: 'var(--color-safety-yellow)' }} />
                <div className="flex-1">
                  <p className="text-xs font-bold mb-2 uppercase tracking-wide" style={{ color: 'var(--color-safety-yellow)' }}>
                    🤖 AI-Generated Repair Plan & Materials
                  </p>
                  <div className="text-base text-white whitespace-pre-wrap leading-relaxed">
                    {workOrder.material_suggestion}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Full Contractor Info */}
          {hasContractor && (
            <div className="mb-4 p-4 glass border border-purple-500/30 rounded-lg">
              <p className="text-xs font-bold text-purple-400 mb-3 uppercase tracking-wide">
                Contractor Information
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                <div>
                  <p className="text-gray-400">Name:</p>
                  <p className="text-white font-bold text-base">{workOrder.contractor_name}</p>
                </div>
                {workOrder.contractor_specialty && (
                  <div>
                    <p className="text-gray-400">Specialty:</p>
                    <p className="text-white font-medium capitalize">
                      {workOrder.contractor_specialty.replace('_', ' ')}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Contractor Selection - Only show if no contractor assigned and pending */}
      {!hasContractor && isPending && contractors.length > 0 && (
        <div className="mb-4 p-4 glass border border-gray-500/30 rounded-lg">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Select Contractor
          </label>
          <select
            value={selectedContractor}
            onChange={(e) => setSelectedContractor(e.target.value)}
            className="w-full px-3 py-2 glass border border-gray-500/30 rounded-lg text-white focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 mb-3 bg-transparent"
          >
            <option value="" className="bg-slate-800">Choose a contractor...</option>
            {contractors.map((contractor) => (
              <option key={contractor.id} value={contractor.id} className="bg-slate-800">
                {contractor.name} - {contractor.specialty.replace('_', ' ')} {contractor.rating && `(⭐ ${contractor.rating})`}
              </option>
            ))}
          </select>
          <button
            onClick={handleAssignContractor}
            disabled={!selectedContractor || isAssigning}
            className={`w-full py-2 px-4 rounded-lg font-medium transition-all duration-300 ${
              selectedContractor && !isAssigning
                ? 'bg-gradient-to-r from-purple-500 to-indigo-500 text-white hover:from-purple-600 hover:to-indigo-600 shadow-lg shadow-purple-500/30'
                : 'glass border border-gray-500/30 text-gray-500 cursor-not-allowed'
            }`}
          >
            {isAssigning ? 'Assigning...' : 'Assign Contractor'}
          </button>
        </div>
      )}

      {/* Action Button */}
      {isPending && hasContractor && (
        <button
          onClick={handleApprove}
          disabled={isApproving}
          className={`w-full py-2 px-4 rounded-lg font-medium transition-all duration-300 ${
            isApproving
              ? 'glass border border-gray-500/30 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-green-500 to-emerald-500 text-white hover:from-green-600 hover:to-emerald-600 shadow-lg shadow-green-500/30'
          }`}
        >
          {isApproving ? (
            <span className="flex items-center justify-center">
              <Clock className="animate-spin h-4 w-4 mr-2" />
              Approving...
            </span>
          ) : (
            <span className="flex items-center justify-center">
              <CheckCircle className="h-4 w-4 mr-2" />
              Approve & Send to Contractor
            </span>
          )}
        </button>
      )}

      {isApproved && (
        <div className="flex items-center justify-center text-green-400 py-2 glass border border-green-500/30 rounded-lg">
          <CheckCircle className="h-5 w-5 mr-2" />
          <span className="font-medium">Work Order Approved & Sent</span>
        </div>
      )}
      </div>

      {/* Image Modal */}
      {showImage && workOrder.issue?.image_url && (
        <div
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={() => setShowImage(false)}
        >
          <div className="relative max-w-4xl max-h-full">
            <button
              onClick={() => setShowImage(false)}
              className="absolute -top-10 right-0 text-white hover:text-gray-300 text-xl font-bold"
            >
              ✕
            </button>
            <img
              src={getImageUrl(workOrder.issue.image_url)}
              alt="Issue"
              className="max-w-full max-h-[90vh] object-contain rounded-lg shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            />
            <p className="text-white text-center mt-2 text-sm">Click outside to close</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkOrderCard;
