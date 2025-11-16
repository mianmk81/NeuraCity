import { Loader2 } from 'lucide-react';

const LoadingSpinner = ({ size = 'md', text = 'Loading...' }) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16',
  };

  return (
    <div className="flex flex-col items-center justify-center py-8">
      <Loader2 className={`${sizeClasses[size]} text-cyan-400 animate-spin`} />
      {text && (
        <p className="mt-4 text-gray-300 text-sm animate-pulse">{text}</p>
      )}
    </div>
  );
};

export default LoadingSpinner;
