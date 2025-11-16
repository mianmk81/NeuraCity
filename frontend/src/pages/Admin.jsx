import { AlertTriangle, CheckCircle, Eye, List, Loader2, Wrench, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import WorkOrderCard from '../components/WorkOrderCard';
import { approveWorkOrder, getEmergencyQueue, getIssues, getWorkOrders, markEmergencyReviewed, updateIssueStatus } from '../lib/api';
import { formatDate, formatIssueType, getIssueCategoryName, getPriorityColor } from '../lib/helpers';

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
    <div className="min-h-screen py-4 md:py-8 relative z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-4 md:mb-8">
          <h1 className="text-2xl md:text-3xl font-bold text-white mb-2 neon-blue">
            Admin Dashboard
          </h1>
          <p className="text-sm md:text-base text-gray-300">
            Manage emergencies, work orders, and infrastructure issues
          </p>
        </div>

        {/* Tabs */}
        <div className="glass rounded-lg shadow mb-4 md:mb-6 border border-blue-500/30 overflow-x-auto">
          <div className="border-b border-blue-500/30">
            <nav className="flex -mb-px min-w-max md:min-w-0">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;

                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center px-4 md:px-6 py-3 md:py-4 text-sm font-medium border-b-2 transition-colors whitespace-nowrap min-h-[44px] ${
                      isActive
                        ? 'border-cyan-500 text-cyan-400 neon-cyan'
                        : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-500/50'
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
          <div className="mb-6 glass border border-red-500/30 rounded-lg p-4">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-12 w-12 text-cyan-400 animate-spin" />
          </div>
        ) : (
          <>
            {/* Emergency Queue Tab */}
            {activeTab === 'emergency' && (
              <div className="space-y-6">
                {emergencyQueue.length === 0 ? (
                  <div className="glass rounded-lg shadow p-12 text-center border border-blue-500/30">
                    <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-300">No emergency items in queue</p>
                  </div>
                ) : (
                  emergencyQueue.map((emergency) => {
                    const categoryName = emergency.issue
                      ? getIssueCategoryName(emergency.issue.issue_type, emergency.issue.description)
                      : 'Emergency Report';

                    return (
                    <div key={emergency.id} className="glass rounded-lg shadow border border-red-500/30 p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="text-lg md:text-xl font-bold text-white mb-1">
                            {categoryName}
                          </h3>
                          <p className="text-sm text-gray-400">
                            {formatDate(emergency.created_at)}
                          </p>
                          {emergency.issue?.location_name && (
                            <p className="text-sm text-cyan-400 mt-1 flex items-center">
                              <span className="mr-1">📍</span>
                              {emergency.issue.location_name}
                            </p>
                          )}
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium border ${
                          emergency.status === 'reviewed'
                            ? 'bg-green-500/20 text-green-400 border-green-500/50'
                            : 'bg-red-500/20 text-red-400 border-red-500/50'
                        }`}>
                          {emergency.status.toUpperCase()}
                        </span>
                      </div>

                      {emergency.issue && (
                        <div className="mb-4 p-3 glass border border-blue-500/20 rounded-lg">
                          <p className="text-sm text-gray-300">
                            <span className="font-medium text-cyan-400">Location:</span>{' '}
                            {emergency.issue.lat.toFixed(6)}, {emergency.issue.lng.toFixed(6)}
                          </p>
                          <p className="text-sm text-gray-300">
                            <span className="font-medium text-cyan-400">Type:</span>{' '}
                            {formatIssueType(emergency.issue.issue_type)}
                          </p>
                          {emergency.issue.description && (
                            <p className="text-sm text-gray-300 mt-1">
                              <span className="font-medium text-cyan-400">Description:</span>{' '}
                              {emergency.issue.description}
                            </p>
                          )}
                          {emergency.issue.image_url && (
                            <div className="mt-2">
                              <button
                                onClick={() => setSelectedImage(getImageUrl(emergency.issue.image_url))}
                                className="flex items-center text-cyan-400 hover:text-cyan-300 font-medium text-sm transition-colors"
                              >
                                <Eye className="h-4 w-4 mr-1" />
                                View Evidence Image
                              </button>
                            </div>
                          )}
                        </div>
                      )}

                      {emergency.summary && (
                        <div className="mb-4 p-4 glass border border-yellow-500/30 rounded-lg">
                          <h4 className="text-sm font-semibold text-yellow-400 mb-2">
                            AI-Generated Dispatcher Summary
                          </h4>
                          <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">
                            {emergency.summary}
                          </p>
                        </div>
                      )}

                      {emergency.status === 'pending' && (
                        <button
                          onClick={() => handleMarkEmergencyReviewed(emergency.id)}
                          className="w-full py-2 px-4 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg hover:from-green-600 hover:to-emerald-600 transition-all font-medium flex items-center justify-center shadow-lg shadow-green-500/30"
                        >
                          <CheckCircle className="h-4 w-4 mr-2" />
                          Mark as Reviewed
                        </button>
                      )}
                    </div>
                    );
                  })
                )}
              </div>
            )}

            {/* Work Orders Tab */}
            {activeTab === 'workorders' && (
              <div className="space-y-6">
                {workOrders.length === 0 ? (
                  <div className="glass rounded-lg shadow p-12 text-center border border-blue-500/30">
                    <Wrench className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-300">No work orders available</p>
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
              <div className="glass rounded-lg shadow border border-blue-500/30 overflow-hidden">
                {allIssues.length === 0 ? (
                  <div className="p-12 text-center">
                    <List className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-300">No issues reported</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto -mx-4 md:mx-0" style={{ WebkitOverflowScrolling: 'touch' }}>
                    <div className="inline-block min-w-full align-middle px-4 md:px-0">
                      <table className="min-w-full divide-y divide-blue-500/20">
                      <thead className="glass border-b border-blue-500/30">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Type
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Location
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Priority
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Status
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Date
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-blue-500/20">
                        {allIssues.map((issue) => {
                          const categoryName = getIssueCategoryName(issue.issue_type, issue.description);

                          return (
                          <tr key={issue.id} className="hover:bg-blue-500/10 transition-colors">
                            <td className="px-6 py-4">
                              <div className="text-sm md:text-base font-bold text-white mb-1">
                                {categoryName}
                              </div>
                              {issue.location_name && (
                                <div className="text-xs text-cyan-400 flex items-center">
                                  <span className="mr-1">📍</span>
                                  {issue.location_name}
                                </div>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-xs text-gray-400 font-mono">
                                {issue.lat.toFixed(4)}, {issue.lng.toFixed(4)}
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span
                                className="px-2 py-1 text-xs font-medium rounded-full border"
                                style={{
                                  backgroundColor: `${getPriorityColor(issue.priority)}20`,
                                  color: getPriorityColor(issue.priority),
                                  borderColor: `${getPriorityColor(issue.priority)}50`,
                                }}
                              >
                                {issue.priority || 'N/A'}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <select
                                value={issue.status}
                                onChange={(e) => handleUpdateIssueStatus(issue.id, e.target.value)}
                                className="text-sm glass border border-gray-500/30 rounded px-2 py-1 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500/50 bg-transparent"
                              >
                                <option value="open" className="bg-slate-800">Open</option>
                                <option value="in_progress" className="bg-slate-800">In Progress</option>
                                <option value="resolved" className="bg-slate-800">Resolved</option>
                              </select>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                              {formatDate(issue.created_at)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm">
                              {issue.image_url && (
                                <button
                                  onClick={() => setSelectedImage(getImageUrl(issue.image_url))}
                                  className="flex items-center text-cyan-400 hover:text-cyan-300 font-medium transition-colors"
                                >
                                  <Eye className="h-4 w-4 mr-1" />
                                  View Image
                                </button>
                              )}
                            </td>
                          </tr>
                          );
                        })}
                      </tbody>
                    </table>
                    </div>
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
