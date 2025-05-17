import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import TryOnPage from './pages/TryOnPage';

// This component handles Chrome extension specific functionality
const ChromeExtension = () => {
  const [clothingImage, setClothingImage] = useState(null);
  const location = useLocation();
  
  useEffect(() => {
    // Check if we're running as a Chrome extension
    if (window.chrome && chrome.storage) {
      // Get stored clothing image if available
      chrome.storage.local.get(['clothingImage'], (result) => {
        if (result.clothingImage) {
          setClothingImage(result.clothingImage);
        }
      });
      
      // Listen for storage changes
      chrome.storage.onChanged.addListener((changes, namespace) => {
        if (namespace === 'local' && changes.clothingImage) {
          setClothingImage(changes.clothingImage.newValue);
        }
      });
    }
  }, []);
  
  // If we're in the extension and have a clothing image, pass it to the TryOnPage
  if (location.pathname.includes('/app') && clothingImage) {
    return <TryOnPage initialClothingImage={clothingImage} />;
  }
  
  // Otherwise, render normally
  return null;
};

export default ChromeExtension;
