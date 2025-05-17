// Add try-on buttons to product images
function addTryOnButtons() {
  // Look for product images on the page
  const productImages = document.querySelectorAll('.product-image, img[id*="product"], img[class*="product"]');
  
  // For each product image found
  productImages.forEach(img => {
    // Check if we've already added a button to this image
    if (img.dataset.tryOnAdded) return;
    
    // Mark that we've processed this image
    img.dataset.tryOnAdded = 'true';
    
    // Create a try-on button
    const tryOnButton = document.createElement('button');
    tryOnButton.className = 'virtual-try-on-button';
    tryOnButton.textContent = 'Try On';
    
    // Style for the button container
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'virtual-try-on-container';
    
    // Add button to container
    buttonContainer.appendChild(tryOnButton);
    
    // Add container next to the image
    if (img.parentNode) {
      img.parentNode.style.position = 'relative';
      img.parentNode.appendChild(buttonContainer);
    }
    
    // Add click event listener
    tryOnButton.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      
      // Capture the product image
      captureClothingImage(img.src);
    });
  });
}

// Capture product image and send to the extension
function captureClothingImage(imageUrl) {
  // Convert image URL to base64
  const img = new Image();
  img.crossOrigin = 'Anonymous';
  
  img.onload = () => {
    const canvas = document.createElement('canvas');
    canvas.width = img.width;
    canvas.height = img.height;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0);
    
    // Get base64 image data
    try {
      const dataUrl = canvas.toDataURL('image/png');
      const base64Data = dataUrl.split(',')[1];
      
      // Send to background script
      chrome.runtime.sendMessage({
        action: 'captureClothingImage',
        imageData: base64Data
      }, (response) => {
        if (response && response.status === 'success') {
          console.log('Image sent to extension successfully');
        } else {
          console.error('Failed to send image to extension');
        }
      });
    } catch (error) {
      console.error('Error processing image:', error);
      
      // If CORS prevents us from converting the image, try the background script approach
      chrome.runtime.sendMessage({
        action: 'captureClothingImage',
        imageUrl: imageUrl
      });
    }
  };
  
  img.onerror = () => {
    console.error('Error loading image for capture');
    // Try sending just the URL as a fallback
    chrome.runtime.sendMessage({
      action: 'captureClothingImage',
      imageUrl: imageUrl
    });
  };
  
  img.src = imageUrl;
}

// Run the main function to add try-on buttons
function init() {
  // Add buttons to existing images
  addTryOnButtons();
  
  // Set up a mutation observer to detect new product images
  const observer = new MutationObserver((mutations) => {
    addTryOnButtons();
  });
  
  // Start observing
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
}

// Initialize after page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
