const MoodLegend = () => {
  return (
    <div className="glass p-4 rounded-lg shadow-lg border border-blue-500/30">
      <h3 className="text-sm font-semibold text-white mb-3">City Mood</h3>
      <div className="space-y-2">
        <div className="flex items-center">
          <div className="w-4 h-4 rounded-full bg-green-500 mr-2 shadow-lg shadow-green-500/50"></div>
          <span className="text-sm text-gray-300">Positive (0.5 to 1.0)</span>
        </div>
        <div className="flex items-center">
          <div className="w-4 h-4 rounded-full bg-yellow-400 mr-2 shadow-lg shadow-yellow-400/50"></div>
          <span className="text-sm text-gray-300">Neutral (0 to 0.5)</span>
        </div>
        <div className="flex items-center">
          <div className="w-4 h-4 rounded-full bg-red-500 mr-2 shadow-lg shadow-red-500/50"></div>
          <span className="text-sm text-gray-300">Negative (-1.0 to 0)</span>
        </div>
      </div>
    </div>
  );
};

export default MoodLegend;
