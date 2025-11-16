const PageSkeleton = () => {
  return (
    <div className="min-h-screen py-12 relative z-10 animate-pulse">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header Skeleton */}
        <div className="mb-8">
          <div className="h-10 bg-gray-700/50 rounded-lg w-1/3 mb-4"></div>
          <div className="h-6 bg-gray-700/30 rounded-lg w-2/3"></div>
        </div>

        {/* Content Grid Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="glass rounded-xl p-6 border border-blue-500/30">
              <div className="h-6 bg-gray-700/50 rounded w-2/3 mb-4"></div>
              <div className="h-4 bg-gray-700/30 rounded w-full mb-2"></div>
              <div className="h-4 bg-gray-700/30 rounded w-5/6"></div>
            </div>
          ))}
        </div>

        {/* Large Content Block Skeleton */}
        <div className="glass rounded-xl p-8 border border-blue-500/30">
          <div className="h-8 bg-gray-700/50 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            <div className="h-4 bg-gray-700/30 rounded w-full"></div>
            <div className="h-4 bg-gray-700/30 rounded w-11/12"></div>
            <div className="h-4 bg-gray-700/30 rounded w-10/12"></div>
            <div className="h-4 bg-gray-700/30 rounded w-full"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PageSkeleton;
