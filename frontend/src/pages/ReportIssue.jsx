import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import IssueForm from '../components/IssueForm';
import { reportIssue } from '../lib/api';
import { CheckCircle, AlertTriangle, TrendingUp } from 'lucide-react';

const ReportIssue = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleSubmit = async (formData) => {
    setLoading(true);
    setError(null);

    try {
      const result = await reportIssue(formData);
      setSuccess(result);

      // Auto redirect after 5 seconds
      setTimeout(() => {
        navigate('/');
      }, 5000);
    } catch (err) {
      setError(err.message || 'Failed to submit issue. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="h-10 w-10 text-green-600" />
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                Issue Reported Successfully
              </h2>
              <p className="text-gray-600">
                Thank you for helping improve our city
              </p>
            </div>

            <div className="border-t border-b border-gray-200 py-6 mb-6">
              <h3 className="font-semibold text-gray-900 mb-4">
                Report Details
              </h3>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Issue Type</span>
                  <span className="text-sm font-medium text-gray-900">
                    {success.issue_type}
                  </span>
                </div>

                {success.severity !== undefined && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 flex items-center">
                      <AlertTriangle className="h-4 w-4 mr-1" />
                      Severity Score
                    </span>
                    <span className={`text-sm font-medium ${
                      success.severity > 0.7 ? 'text-red-600' :
                      success.severity > 0.4 ? 'text-yellow-600' :
                      'text-green-600'
                    }`}>
                      {success.severity.toFixed(2)}
                    </span>
                  </div>
                )}

                {success.urgency !== undefined && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 flex items-center">
                      <TrendingUp className="h-4 w-4 mr-1" />
                      Urgency Score
                    </span>
                    <span className={`text-sm font-medium ${
                      success.urgency > 0.7 ? 'text-red-600' :
                      success.urgency > 0.4 ? 'text-yellow-600' :
                      'text-green-600'
                    }`}>
                      {success.urgency.toFixed(2)}
                    </span>
                  </div>
                )}

                {success.priority && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Priority</span>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      success.priority === 'critical' ? 'bg-red-100 text-red-700' :
                      success.priority === 'high' ? 'bg-orange-100 text-orange-700' :
                      success.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-green-100 text-green-700'
                    }`}>
                      {success.priority.toUpperCase()}
                    </span>
                  </div>
                )}

                {success.action_type && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Action Type</span>
                    <span className="text-sm font-medium text-gray-900">
                      {success.action_type}
                    </span>
                  </div>
                )}

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Status</span>
                  <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                    {success.status || 'OPEN'}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <p className="text-sm text-blue-800">
                <strong>What happens next?</strong><br />
                {success.action_type === 'emergency_summary' &&
                  'Our emergency team has been notified and will review this report immediately.'}
                {success.action_type === 'work_order' &&
                  'A work order has been generated and will be assigned to the appropriate contractor.'}
                {!success.action_type &&
                  'Your report has been logged and will be reviewed by our team.'}
              </p>
            </div>

            <div className="flex space-x-4">
              <button
                onClick={() => navigate('/')}
                className="flex-1 px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
              >
                Return Home
              </button>
              <button
                onClick={() => window.location.reload()}
                className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors"
              >
                Report Another Issue
              </button>
            </div>

            <p className="text-xs text-gray-500 text-center mt-4">
              Redirecting to home in 5 seconds...
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Report Infrastructure Issue
            </h1>
            <p className="text-gray-600">
              Help improve our city by reporting problems with image evidence and GPS location
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-start">
                <AlertTriangle className="h-5 w-5 text-red-600 mr-2 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="text-sm font-medium text-red-800 mb-1">
                    Submission Failed
                  </h3>
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-blue-900 mb-2">
              Required Information
            </h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Photo evidence of the issue</li>
              <li>• GPS location (automatic)</li>
              <li>• Issue type (accident, pothole, traffic light, or other)</li>
            </ul>
          </div>

          <IssueForm onSubmit={handleSubmit} loading={loading} />
        </div>
      </div>
    </div>
  );
};

export default ReportIssue;
