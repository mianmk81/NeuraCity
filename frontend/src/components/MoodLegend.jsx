const MoodLegend = () => {
  return (
    <div className="bg-white p-4 rounded-lg shadow-lg">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">City Mood</h3>
      <div className="space-y-2">
        <div className="flex items-center">
          <div className="w-4 h-4 rounded-full bg-green-500 mr-2"></div>
          <span className="text-sm text-gray-600">Positive (0.5 to 1.0)</span>
        </div>
        <div className="flex items-center">
          <div className="w-4 h-4 rounded-full bg-yellow-400 mr-2"></div>
          <span className="text-sm text-gray-600">Neutral (0 to 0.5)</span>
        </div>
        <div className="flex items-center">
          <div className="w-4 h-4 rounded-full bg-red-500 mr-2"></div>
          <span className="text-sm text-gray-600">Negative (-1.0 to 0)</span>
        </div>
      </div>
    </div>
  );
};

export default MoodLegend;
