import React from 'react';

const LoadingSpinner = ({ size = 'md', text = 'Loading...' }) => {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };
  
  return (
    <div className="flex flex-col items-center justify-center">
      <div className={`${sizes[size]} animate-spin rounded-full border-4 border-white border-t-accent`}></div>
      {text && <p className="mt-2 text-white text-sm">{text}</p>}
    </div>
  );
};

export default LoadingSpinner;
