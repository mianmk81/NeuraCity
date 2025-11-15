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
      <div className="min-h-screen py-12 relative z-10">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="glass rounded-xl shadow-lg p-8 border border-green-500/30">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-4 glow-box">
                <CheckCircle className="h-10 w-10 text-white" />
              </div>
              <h2 className="text-3xl font-bold text-white mb-2 neon-blue">
                Issue Reported Successfully
              </h2>
              <p className="text-gray-300">
                Thank you for helping improve our city
              </p>
            </div>

            <div className="border-t border-b border-blue-500/30 py-6 mb-6">
              <h3 className="font-semibold text-white mb-4">
                Report Details
              </h3>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-300">Issue Type</span>
                  <span className="text-sm font-medium text-cyan-400">
                    {success.issue_type}
                  </span>
                </div>

                {success.severity !== undefined && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-300 flex items-center">
                      <AlertTriangle className="h-4 w-4 mr-1" />
                      Severity Score
                    </span>
                    <span className={`text-sm font-medium ${
                      success.severity > 0.7 ? 'text-red-400' :
                      success.severity > 0.4 ? 'text-yellow-400' :
                      'text-green-400'
                    }`}>
                      {success.severity.toFixed(2)}
                    </span>
                  </div>
                )}

                {success.urgency !== undefined && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-300 flex items-center">
                      <TrendingUp className="h-4 w-4 mr-1" />
                      Urgency Score
                    </span>
                    <span className={`text-sm font-medium ${
                      success.urgency > 0.7 ? 'text-red-400' :
                      success.urgency > 0.4 ? 'text-yellow-400' :
                      'text-green-400'
                    }`}>
                      {success.urgency.toFixed(2)}
                    </span>
                  </div>
                )}

                {success.priority && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-300">Priority</span>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${
                      success.priority === 'critical' ? 'bg-red-500/20 text-red-400 border-red-500/50' :
                      success.priority === 'high' ? 'bg-orange-500/20 text-orange-400 border-orange-500/50' :
                      success.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50' :
                      'bg-green-500/20 text-green-400 border-green-500/50'
                    }`}>
                      {success.priority.toUpperCase()}
                    </span>
                  </div>
                )}

                {success.action_type && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-300">Action Type</span>
                    <span className="text-sm font-medium text-cyan-400">
                      {success.action_type}
                    </span>
                  </div>
                )}

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-300">Status</span>
                  <span className="px-3 py-1 bg-blue-500/20 text-blue-400 border border-blue-500/50 rounded-full text-xs font-medium">
                    {success.status || 'OPEN'}
                  </span>
                </div>
              </div>
            </div>

            <div className="glass border border-blue-500/30 rounded-lg p-4 mb-6">
              <p className="text-sm text-gray-300">
                <strong className="text-cyan-400">What happens next?</strong><br />
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
                className="flex-1 px-6 py-3 btn-futuristic text-white rounded-lg font-medium transition-all duration-300"
              >
                Return Home
              </button>
              <button
                onClick={() => window.location.reload()}
                className="flex-1 px-6 py-3 glass border border-gray-500/30 text-gray-300 rounded-lg font-medium hover:border-cyan-500/50 hover:text-cyan-400 transition-all duration-300"
              >
                Report Another Issue
              </button>
            </div>

            <p className="text-xs text-gray-400 text-center mt-4">
              Redirecting to home in 5 seconds...
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-6 md:py-12 relative z-10">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="glass rounded-xl shadow-lg p-4 md:p-8 border border-blue-500/30">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2 neon-blue">
              Report Infrastructure Issue
            </h1>
            <p className="text-gray-300">
              Help improve our city by reporting problems with image evidence and GPS location
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 glass border border-red-500/30 rounded-lg">
              <div className="flex items-start">
                <AlertTriangle className="h-5 w-5 text-red-400 mr-2 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="text-sm font-medium text-red-400 mb-1">
                    Submission Failed
                  </h3>
                  <p className="text-sm text-gray-300">{error}</p>
                </div>
              </div>
            </div>
          )}

          <div className="mb-6 glass border border-blue-500/30 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-cyan-400 mb-2">
              Required Information
            </h3>
            <ul className="text-sm text-gray-300 space-y-1">
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
