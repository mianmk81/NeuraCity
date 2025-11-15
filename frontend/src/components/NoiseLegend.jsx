const NoiseLegend = () => {
  return (
    <div className="bg-white p-4 rounded-lg shadow-lg">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">Noise Levels</h3>
      <div className="space-y-2">
        <div className="flex items-center">
          <div className="w-4 h-4 rounded-full bg-green-500 mr-2"></div>
          <span className="text-sm text-gray-600">Quiet (40-55 dB)</span>
        </div>
        <div className="flex items-center">
          <div className="w-4 h-4 rounded-full bg-yellow-400 mr-2"></div>
          <span className="text-sm text-gray-600">Moderate (55-70 dB)</span>
        </div>
        <div className="flex items-center">
          <div className="w-4 h-4 rounded-full bg-red-500 mr-2"></div>
          <span className="text-sm text-gray-600">Loud (70-85 dB)</span>
        </div>
      </div>
    </div>
  );
};

export default NoiseLegend;
