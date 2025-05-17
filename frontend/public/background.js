// Listen for installation
chrome.runtime.onInstalled.addListener(() => {
  console.log('Virtual Try-On Extension installed');
});

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'captureClothingImage') {
    // When a clothing image is captured, store it in chrome.storage
    chrome.storage.local.set({ 'clothingImage': request.imageData }, () => {
      console.log('Clothing image saved to storage');
      
      // Open the try-on popup
      chrome.windows.create({
        url: chrome.runtime.getURL('index.html#/app'),
        type: 'popup',
        width: 1200,
        height: 800
      });
    });
    
    // Tell the content script we're processing
    sendResponse({ status: 'success' });
    return true; // Keep the message channel open for async response
  }
});
