import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import "./App.css";
import Navbar from "./components/Navbar";
import HomePage from "./pages/HomePage";
import TryOnPage from "./pages/TryOnPage";
import ChromeExtension from "./ChromeExtension";

function App() {
  // Detect if we're running as a Chrome extension
  const isExtension = !!window.chrome && !!chrome.runtime && !!chrome.runtime.id;

  return (
    <div className="App">
      <BrowserRouter>
        {!isExtension && <Navbar />}
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/app" element={<TryOnPage />} />
        </Routes>
        <ChromeExtension />
      </BrowserRouter>
      <ToastContainer 
        position="bottom-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="dark"
      />
    </div>
  );
}

export default App;
