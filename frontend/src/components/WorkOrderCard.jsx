import { useState } from 'react';
import { CheckCircle, Clock, Wrench, Package, User } from 'lucide-react';
import { formatDate, formatIssueType } from '../lib/helpers';

const WorkOrderCard = ({ workOrder, onApprove }) => {
  const [isApproving, setIsApproving] = useState(false);

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

  const isApproved = workOrder.status === 'approved';
  const isPending = workOrder.status === 'pending_review';

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
        </div>
      )}

      {/* Material Suggestion */}
      {workOrder.material_suggestion && (
        <div className="mb-4 p-3 bg-blue-50 rounded-lg">
          <div className="flex items-start">
            <Package className="h-5 w-5 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-xs font-medium text-blue-600 mb-1">
                Materials Suggested
              </p>
              <p className="text-sm text-blue-800">
                {workOrder.material_suggestion}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Contractor Info */}
      {workOrder.contractor && (
        <div className="mb-4 p-3 bg-purple-50 rounded-lg">
          <div className="flex items-start">
            <User className="h-5 w-5 text-purple-600 mr-2 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-xs font-medium text-purple-600 mb-1">
                Assigned Contractor
              </p>
              <p className="text-sm font-medium text-purple-800">
                {workOrder.contractor.name}
              </p>
              <p className="text-xs text-purple-700">
                {workOrder.contractor.specialty}
              </p>
              <p className="text-xs text-purple-600 mt-1">
                {workOrder.contractor.contact_email}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Action Button */}
      {isPending && (
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
              Approve Work Order
            </span>
          )}
        </button>
      )}

      {isApproved && (
        <div className="flex items-center justify-center text-green-600 py-2">
          <CheckCircle className="h-5 w-5 mr-2" />
          <span className="font-medium">Work Order Approved</span>
        </div>
      )}
    </div>
  );
};

export default WorkOrderCard;
