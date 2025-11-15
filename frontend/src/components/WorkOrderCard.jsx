import { useState, useEffect } from 'react';
import { CheckCircle, Clock, Wrench, Package, User, Eye } from 'lucide-react';
import { formatDate, formatIssueType } from '../lib/helpers';
import { getContractors, assignContractor } from '../lib/api';

const WorkOrderCard = ({ workOrder, onApprove, onUpdate }) => {
  const [isApproving, setIsApproving] = useState(false);
  const [contractors, setContractors] = useState([]);
  const [selectedContractor, setSelectedContractor] = useState(workOrder.contractor_id || '');
  const [isAssigning, setIsAssigning] = useState(false);
  const [showImage, setShowImage] = useState(false);

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

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200 p-5">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">
            {formatIssueType(workOrder.issue?.issue_type || 'Unknown')}
          </h3>
          <p className="text-sm text-gray-500">
            {formatDate(workOrder.created_at)}
          </p>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
          isApproved ? 'bg-green-100 text-green-700' :
          isPending ? 'bg-yellow-100 text-yellow-700' :
          'bg-gray-100 text-gray-700'
        }`}>
          {workOrder.status.replace('_', ' ').toUpperCase()}
        </span>
      </div>

      {/* Issue Location */}
      {workOrder.issue && (
        <div className="mb-4 text-sm text-gray-600">
          <p>
            <span className="font-medium">Location:</span>{' '}
            {workOrder.issue.lat.toFixed(6)}, {workOrder.issue.lng.toFixed(6)}
          </p>
          {workOrder.issue.description && (
            <p className="mt-1">
              <span className="font-medium">Description:</span>{' '}
              {workOrder.issue.description}
            </p>
          )}
          {workOrder.issue.image_url && (
            <button
              onClick={() => setShowImage(true)}
              className="mt-2 flex items-center text-primary-600 hover:text-primary-800 font-medium text-sm"
            >
              <Eye className="h-4 w-4 mr-1" />
              View Issue Image
            </button>
          )}
        </div>
      )}

      {/* Material Suggestion with Better Formatting */}
      {workOrder.material_suggestion && (
        <div className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-start">
            <Package className="h-5 w-5 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-xs font-semibold text-blue-700 mb-2 uppercase">
                AI-Generated Repair Plan
              </p>
              <div className="text-sm text-blue-900 whitespace-pre-wrap leading-relaxed">
                {workOrder.material_suggestion}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Contractor Selection or Info */}
      {hasContractor ? (
        <div className="mb-4 p-3 bg-purple-50 rounded-lg border border-purple-200">
          <div className="flex items-start">
            <User className="h-5 w-5 text-purple-600 mr-2 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-xs font-medium text-purple-600 mb-1">
                Assigned Contractor
              </p>
              <p className="text-sm font-medium text-purple-900">
                {workOrder.contractor_name || 'Contractor'}
              </p>
              <p className="text-xs text-purple-700 capitalize">
                Specialty: {(workOrder.contractor_specialty || 'general').replace('_', ' ')}
              </p>
            </div>
          </div>
        </div>
      ) : isPending && contractors.length > 0 && (
        <div className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-300">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Contractor
          </label>
          <select
            value={selectedContractor}
            onChange={(e) => setSelectedContractor(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent mb-3"
          >
            <option value="">Choose a contractor...</option>
            {contractors.map((contractor) => (
              <option key={contractor.id} value={contractor.id}>
                {contractor.name} - {contractor.specialty.replace('_', ' ')} {contractor.rating && `(⭐ ${contractor.rating})`}
              </option>
            ))}
          </select>
          <button
            onClick={handleAssignContractor}
            disabled={!selectedContractor || isAssigning}
            className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
              selectedContractor && !isAssigning
                ? 'bg-purple-600 text-white hover:bg-purple-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
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
          className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
            isApproving
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-green-600 text-white hover:bg-green-700'
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
        <div className="flex items-center justify-center text-green-600 py-2 bg-green-50 rounded-lg">
          <CheckCircle className="h-5 w-5 mr-2" />
          <span className="font-medium">Work Order Approved & Sent</span>
        </div>
      )}

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
