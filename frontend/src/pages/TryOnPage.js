import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';
import ImageUploader from '../components/ImageUploader';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TryOnPage = () => {
  // State for image uploads
  const [personImage, setPersonImage] = useState(null);
  const [clothingImage, setClothingImage] = useState(null);
  
  // State for results
  const [resultImage, setResultImage] = useState(null);
  
  // Loading state
  const [isLoading, setIsLoading] = useState(false);

  // Handle person image upload
  const handlePersonImageUpload = (base64String, fileName) => {
    setPersonImage(base64String);
    toast.success('Person image uploaded successfully');
  };

  // Handle clothing image upload
  const handleClothingImageUpload = (base64String, fileName) => {
    setClothingImage(base64String);
    toast.success('Clothing image uploaded successfully');
  };

  // Handle try-on process
  const handleTryOn = async () => {
    if (!personImage || !clothingImage) {
      toast.error('Please upload both a person image and a clothing image');
      return;
    }

    setIsLoading(true);
    setResultImage(null);
    
    try {
      const response = await axios.post(`${API}/try-on`, {
        person_image: personImage,
        clothing_image: clothingImage
      });
      
      if (response.data && response.data.result_image) {
        setResultImage(response.data.result_image);
        toast.success('Virtual try-on completed successfully!');
      } else {
        toast.error('Failed to generate try-on result');
      }
    } catch (error) {
      console.error('Try-on error:', error);
      toast.error(error.response?.data?.detail || 'An error occurred during the try-on process');
    } finally {
      setIsLoading(false);
    }
  };

  // Animation variants
  const pageVariants = {
    initial: { opacity: 0 },
    animate: { 
      opacity: 1,
      transition: { duration: 0.5 }
    },
    exit: { opacity: 0 }
  };

  return (
    <motion.div 
      className="min-h-screen bg-gradient-to-b from-background to-background-light text-white py-10 px-4 sm:px-6 lg:px-8"
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageVariants}
    >
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8">Virtual Try-On</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left side - Image uploads */}
          <div className="bg-background-light p-6 rounded-lg shadow-lg">
            <h2 className="text-xl font-semibold mb-4">Upload Images</h2>
            
            <ImageUploader 
              onImageUpload={handlePersonImageUpload}
              label="Upload Your Photo"
            />
            
            {personImage && (
              <div className="mt-4 p-4 bg-background rounded-lg">
                <p className="text-sm text-gray-300 mb-2">Preview:</p>
                <img 
                  src={`data:image/jpeg;base64,${personImage}`} 
                  alt="Person" 
                  className="max-h-40 max-w-full object-contain mx-auto rounded"
                />
              </div>
            )}
            
            <div className="mt-6">
              <ImageUploader 
                onImageUpload={handleClothingImageUpload}
                label="Upload Clothing Item"
              />
              
              {clothingImage && (
                <div className="mt-4 p-4 bg-background rounded-lg">
                  <p className="text-sm text-gray-300 mb-2">Preview:</p>
                  <img 
                    src={`data:image/jpeg;base64,${clothingImage}`} 
                    alt="Clothing" 
                    className="max-h-40 max-w-full object-contain mx-auto rounded"
                  />
                </div>
              )}
            </div>
            
            <div className="mt-6">
              <Button 
                onClick={handleTryOn} 
                disabled={!personImage || !clothingImage || isLoading}
                fullWidth
                variant="accent"
                size="lg"
              >
                {isLoading ? <LoadingSpinner size="sm" text="" /> : 'Generate Try-On'}
              </Button>
            </div>
          </div>
          
          {/* Right side - Results */}
          <div className="bg-background-light p-6 rounded-lg shadow-lg flex flex-col">
            <h2 className="text-xl font-semibold mb-4">Try-On Result</h2>
            
            <div className="flex-grow flex items-center justify-center bg-background rounded-lg p-4">
              {isLoading ? (
                <LoadingSpinner text="Generating your virtual try-on..." />
              ) : resultImage ? (
                <div className="text-center">
                  <img 
                    src={`data:image/jpeg;base64,${resultImage}`} 
                    alt="Try-on result" 
                    className="max-w-full max-h-[60vh] object-contain rounded-lg shadow-md"
                  />
                  <p className="mt-4 text-sm text-gray-300">
                    Generated using AI-powered technology
                  </p>
                </div>
              ) : (
                <div className="text-center text-gray-400">
                  <p>Upload your photo and a clothing item, then click "Generate Try-On" to see the result</p>
                </div>
              )}
            </div>
            
            {resultImage && (
              <div className="mt-4">
                <Button variant="primary" fullWidth>
                  Save Result
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default TryOnPage;
