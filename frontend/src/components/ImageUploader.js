import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FaUpload, FaImage } from 'react-icons/fa';

const ImageUploader = ({ onImageUpload, label, maxSize = 5242880, accept = 'image/*' }) => {
  const onDrop = useCallback(acceptedFiles => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      const reader = new FileReader();
      
      reader.onload = () => {
        // Convert to base64 string (remove data:image/jpeg;base64, prefix)
        const base64String = reader.result.split(',')[1];
        onImageUpload(base64String, file.name);
      };
      
      reader.readAsDataURL(file);
    }
  }, [onImageUpload]);

  const { getRootProps, getInputProps, isDragActive, isDragReject, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png']
    },
    maxSize,
    multiple: false
  });

  const fileRejectionItems = fileRejections.map(({ file, errors }) => (
    <div key={file.path} className="text-red-500 text-sm mt-2">
      {errors.map(e => (
        <p key={e.code}>{e.message}</p>
      ))}
    </div>
  ));

  return (
    <div className="mb-4">
      {label && <label className="block text-white text-sm font-medium mb-2">{label}</label>}
      
      <div 
        {...getRootProps()} 
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors duration-200
          ${isDragActive ? 'border-accent bg-accent/10' : 'border-gray-600 hover:border-accent'}
          ${isDragReject ? 'border-red-500' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center justify-center text-gray-300">
          {isDragActive ? (
            <FaUpload className="w-10 h-10 mb-3 text-accent" />
          ) : (
            <FaImage className="w-10 h-10 mb-3" />
          )}
          
          <p className="mb-2">
            {isDragActive 
              ? 'Drop the image here...' 
              : 'Drag and drop an image here, or click to select a file'}
          </p>
          <p className="text-xs text-gray-400">
            (Max file size: {Math.floor(maxSize / (1024 * 1024))}MB)
          </p>
        </div>
      </div>
      
      {fileRejectionItems}
    </div>
  );
};

export default ImageUploader;
