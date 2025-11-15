import { AlertTriangle, CheckCircle, Eye, List, Loader2, Wrench, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import WorkOrderCard from '../components/WorkOrderCard';
import { approveWorkOrder, getEmergencyQueue, getIssues, getWorkOrders, markEmergencyReviewed, updateIssueStatus } from '../lib/api';
import { formatDate, formatIssueType, getPriorityColor } from '../lib/helpers';

// Helper function to get full image URL
const getImageUrl = (imageUrl) => {
  if (!imageUrl) return null;
  if (imageUrl.startsWith('http')) return imageUrl;
  const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
  const backendURL = baseURL.replace('/api/v1', '');
  return `${backendURL}/${imageUrl}`;
};

const Admin = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [activeTab, setActiveTab] = useState('emergency');
  const [emergencyQueue, setEmergencyQueue] = useState([]);
  const [workOrders, setWorkOrders] = useState([]);
  const [allIssues, setAllIssues] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const tabs = [
    { id: 'emergency', label: 'Emergency Queue', icon: AlertTriangle },
    { id: 'workorders', label: 'Work Orders', icon: Wrench },
    { id: 'issues', label: 'All Issues', icon: List },
  ];

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      if (activeTab === 'emergency') {
        const data = await getEmergencyQueue();
        setEmergencyQueue(data);
      } else if (activeTab === 'workorders') {
        const data = await getWorkOrders();
        setWorkOrders(data);
      } else if (activeTab === 'issues') {
        const data = await getIssues();
        setAllIssues(data);
      }
    } catch (err) {
      setError(err.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleApproveWorkOrder = async (id) => {
    try {
      await approveWorkOrder(id);
      // Refresh work orders
      fetchData();
    } catch (err) {
      alert(err.message || 'Failed to approve work order');
    }
  };

  const handleWorkOrderUpdate = (updatedWorkOrder) => {
    // Update the work order in state without refetching
    setWorkOrders(orders => 
      orders.map(order => order.id === updatedWorkOrder.id ? updatedWorkOrder : order)
    );
  };

  const handleMarkEmergencyReviewed = async (id) => {
    try {
      await markEmergencyReviewed(id);
      // Refresh emergency queue
      fetchData();
    } catch (err) {
      alert(err.message || 'Failed to mark emergency as reviewed');
    }
  };

  const handleUpdateIssueStatus = async (id, status) => {
    try {
      await updateIssueStatus(id, status);
      // Refresh issues
      fetchData();
    } catch (err) {
      alert(err.message || 'Failed to update issue status');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Admin Dashboard
          </h1>
          <p className="text-gray-600">
            Manage emergencies, work orders, and infrastructure issues
          </p>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;

                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                      isActive
                        ? 'border-primary-600 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="h-5 w-5 mr-2" />
                    {tab.label}
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Content */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-12 w-12 text-primary-600 animate-spin" />
          </div>
        ) : (
          <>
            {/* Emergency Queue Tab */}
            {activeTab === 'emergency' && (
              <div className="space-y-6">
                {emergencyQueue.length === 0 ? (
                  <div className="bg-white rounded-lg shadow p-12 text-center">
                    <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">No emergency items in queue</p>
                  </div>
                ) : (
                  emergencyQueue.map((emergency) => (
                    <div key={emergency.id} className="bg-white rounded-lg shadow border border-gray-200 p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 mb-1">
                            Emergency Report
                          </h3>
                          <p className="text-sm text-gray-500">
                            {formatDate(emergency.created_at)}
                          </p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          emergency.status === 'reviewed'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-red-100 text-red-700'
                        }`}>
                          {emergency.status.toUpperCase()}
                        </span>
                      </div>

                      {emergency.issue && (
                        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                          <p className="text-sm text-gray-600">
                            <span className="font-medium">Location:</span>{' '}
                            {emergency.issue.lat.toFixed(6)}, {emergency.issue.lng.toFixed(6)}
                          </p>
                          <p className="text-sm text-gray-600">
                            <span className="font-medium">Type:</span>{' '}
                            {formatIssueType(emergency.issue.issue_type)}
                          </p>
                          {emergency.issue.description && (
                            <p className="text-sm text-gray-600 mt-1">
                              <span className="font-medium">Description:</span>{' '}
                              {emergency.issue.description}
                            </p>
                          )}
                          {emergency.issue.image_url && (
                            <div className="mt-2">
                              <button
                                onClick={() => setSelectedImage(getImageUrl(emergency.issue.image_url))}
                                className="flex items-center text-primary-600 hover:text-primary-800 font-medium text-sm"
                              >
                                <Eye className="h-4 w-4 mr-1" />
                                View Evidence Image
                              </button>
                            </div>
                          )}
                        </div>
                      )}

                      {emergency.summary && (
                        <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                          <h4 className="text-sm font-semibold text-yellow-900 mb-2">
                            AI-Generated Dispatcher Summary
                          </h4>
                          <p className="text-sm text-yellow-800 leading-relaxed whitespace-pre-wrap">
                            {emergency.summary}
                          </p>
                        </div>
                      )}

                      {emergency.status === 'pending' && (
                        <button
                          onClick={() => handleMarkEmergencyReviewed(emergency.id)}
                          className="w-full py-2 px-4 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium flex items-center justify-center"
                        >
                          <CheckCircle className="h-4 w-4 mr-2" />
                          Mark as Reviewed
                        </button>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Work Orders Tab */}
            {activeTab === 'workorders' && (
              <div className="space-y-6">
                {workOrders.length === 0 ? (
                  <div className="bg-white rounded-lg shadow p-12 text-center">
                    <Wrench className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">No work orders available</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {workOrders.map((workOrder) => (
                      <WorkOrderCard
                        key={workOrder.id}
                        workOrder={workOrder}
                        onApprove={handleApproveWorkOrder}
                        onUpdate={handleWorkOrderUpdate}
                      />
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* All Issues Tab */}
            {activeTab === 'issues' && (
              <div className="bg-white rounded-lg shadow">
                {allIssues.length === 0 ? (
                  <div className="p-12 text-center">
                    <List className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">No issues reported</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Type
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Location
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Priority
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Status
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Date
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {allIssues.map((issue) => (
                          <tr key={issue.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm font-medium text-gray-900">
                                {formatIssueType(issue.issue_type)}
                              </div>
                              {issue.description && (
                                <div className="text-xs text-gray-500 max-w-xs truncate">
                                  {issue.description}
                                </div>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-xs text-gray-500">
                                {issue.lat.toFixed(4)}, {issue.lng.toFixed(4)}
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span
                                className="px-2 py-1 text-xs font-medium rounded-full"
                                style={{
                                  backgroundColor: `${getPriorityColor(issue.priority)}20`,
                                  color: getPriorityColor(issue.priority),
                                }}
                              >
                                {issue.priority || 'N/A'}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <select
                                value={issue.status}
                                onChange={(e) => handleUpdateIssueStatus(issue.id, e.target.value)}
                                className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-primary-500"
                              >
                                <option value="open">Open</option>
                                <option value="in_progress">In Progress</option>
                                <option value="resolved">Resolved</option>
                              </select>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {formatDate(issue.created_at)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm">
                              {issue.image_url && (
                                <button
                                  onClick={() => setSelectedImage(getImageUrl(issue.image_url))}
                                  className="flex items-center text-primary-600 hover:text-primary-800 font-medium"
                                >
                                  <Eye className="h-4 w-4 mr-1" />
                                  View Image
                                </button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
      
      {/* Image Modal */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div className="relative max-w-4xl max-h-full">
            <button
              onClick={() => setSelectedImage(null)}
              className="absolute -top-10 right-0 text-white hover:text-gray-300 transition-colors"
            >
              <X className="h-8 w-8" />
            </button>
            <img
              src={selectedImage}
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

export default Admin;
