import { useState } from 'react';
import ImageUpload from './ImageUpload';
import GPSCapture from './GPSCapture';
import { AlertCircle } from 'lucide-react';

const ISSUE_TYPES = [
  { value: 'accident', label: 'Accident' },
  { value: 'pothole', label: 'Pothole' },
  { value: 'traffic_light', label: 'Traffic Light' },
  { value: 'other', label: 'Other' },
];

const IssueForm = ({ onSubmit, loading = false }) => {
  const [image, setImage] = useState(null);
  const [location, setLocation] = useState(null);
  const [issueType, setIssueType] = useState('');
  const [customType, setCustomType] = useState('');
  const [description, setDescription] = useState('');
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};

    if (!image) {
      newErrors.image = 'Image is required';
    }

    if (!location) {
      newErrors.location = 'GPS location is required';
    }

    if (!issueType) {
      newErrors.issueType = 'Issue type is required';
    }

    if (issueType === 'other' && !customType.trim()) {
      newErrors.customType = 'Please specify the issue type';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    // Prepare form data
    const formData = new FormData();
    formData.append('image', image);
    formData.append('lat', location.lat);
    formData.append('lng', location.lng);
    formData.append('issue_type', issueType === 'other' ? customType : issueType);
    if (description.trim()) {
      formData.append('description', description);
    }

    onSubmit(formData);
  };

  const isFormValid = image && location && issueType && (issueType !== 'other' || customType.trim());

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Image Upload */}
      <div>
        <ImageUpload onImageSelect={setImage} required />
        {errors.image && (
          <p className="mt-1 text-sm text-red-600 flex items-center">
            <AlertCircle className="h-4 w-4 mr-1" />
            {errors.image}
          </p>
        )}
      </div>

      {/* GPS Capture */}
      <div>
        <GPSCapture onLocationCapture={setLocation} required />
        {errors.location && (
          <p className="mt-1 text-sm text-red-600 flex items-center">
            <AlertCircle className="h-4 w-4 mr-1" />
            {errors.location}
          </p>
        )}
      </div>

      {/* Issue Type */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Issue Type <span className="text-red-500">*</span>
        </label>
        <select
          value={issueType}
          onChange={(e) => {
            setIssueType(e.target.value);
            setErrors({ ...errors, issueType: undefined });
          }}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          <option value="">Select issue type</option>
          {ISSUE_TYPES.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
        {errors.issueType && (
          <p className="mt-1 text-sm text-red-600 flex items-center">
            <AlertCircle className="h-4 w-4 mr-1" />
            {errors.issueType}
          </p>
        )}
      </div>

      {/* Custom Type Input (shown when "other" is selected) */}
      {issueType === 'other' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Specify Issue Type <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={customType}
            onChange={(e) => {
              setCustomType(e.target.value);
              setErrors({ ...errors, customType: undefined });
            }}
            placeholder="e.g., Street light out, Graffiti, etc."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          {errors.customType && (
            <p className="mt-1 text-sm text-red-600 flex items-center">
              <AlertCircle className="h-4 w-4 mr-1" />
              {errors.customType}
            </p>
          )}
        </div>
      )}

      {/* Description (optional) */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Description <span className="text-gray-400">(optional)</span>
        </label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={4}
          placeholder="Provide additional details about the issue..."
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
        />
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={!isFormValid || loading}
        className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
          isFormValid && !loading
            ? 'bg-primary-600 text-white hover:bg-primary-700'
            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
        }`}
      >
        {loading ? 'Submitting...' : 'Submit Issue Report'}
      </button>

      {!isFormValid && (
        <p className="text-sm text-gray-500 text-center">
          Please complete all required fields to submit
        </p>
      )}
    </form>
  );
};

export default IssueForm;
