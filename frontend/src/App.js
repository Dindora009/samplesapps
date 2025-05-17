import { useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const [appDescription, setAppDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [zipUrl, setZipUrl] = useState(null);
  const [model, setModel] = useState("gpt-4");
  const [logs, setLogs] = useState([]);

  const models = [
    { value: "gpt-4", label: "OpenAI GPT-4" },
    { value: "gpt-4-turbo", label: "OpenAI GPT-4 Turbo" },
    { value: "gpt-3.5-turbo", label: "OpenAI GPT-3.5 Turbo" },
    { value: "claude-3-opus", label: "Anthropic Claude 3 Opus" },
    { value: "claude-3-sonnet", label: "Anthropic Claude 3 Sonnet" }
  ];

  const generateApp = async (e) => {
    e.preventDefault();
    
    if (!appDescription.trim()) {
      setError("Please enter an app description");
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setZipUrl(null);
    setLogs([]);
    
    try {
      // First, initiate the generation process
      const response = await axios.post(`${API}/generate-app`, {
        appDescription,
        model
      });
      
      const { generationId } = response.data;
      
      // Then poll for status updates
      const statusInterval = setInterval(async () => {
        try {
          const statusResponse = await axios.get(`${API}/generation-status/${generationId}`);
          const { status, logs: newLogs, zipUrl: newZipUrl } = statusResponse.data;
          
          if (newLogs && newLogs.length > 0) {
            setLogs(prevLogs => [...prevLogs, ...newLogs]);
          }
          
          if (status === "completed" && newZipUrl) {
            clearInterval(statusInterval);
            setZipUrl(newZipUrl);
            setIsLoading(false);
          } else if (status === "failed") {
            clearInterval(statusInterval);
            setError("App generation failed. Please try again.");
            setIsLoading(false);
          }
        } catch (error) {
          console.error("Error checking generation status:", error);
        }
      }, 3000); // Check every 3 seconds
      
    } catch (error) {
      setIsLoading(false);
      setError(error.response?.data?.message || "Error generating app. Please try again.");
      console.error(error);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="text-center mb-10">
        <h1 className="text-4xl font-bold text-gray-800 mb-3">App Creation Bot</h1>
        <p className="text-xl text-gray-600">
          Describe your app in natural language, and I'll generate the code for you.
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <form onSubmit={generateApp} className="space-y-6">
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="model">
              Select AI Model
            </label>
            <select
              id="model"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={model}
              onChange={(e) => setModel(e.target.value)}
            >
              {models.map((modelOption) => (
                <option key={modelOption.value} value={modelOption.value}>
                  {modelOption.label}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="appDescription">
              App Description
            </label>
            <textarea
              id="appDescription"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 h-32"
              placeholder="Describe your app in detail. For example: 'Create a todo app with user authentication, task categories, due dates, and email reminders.'"
              value={appDescription}
              onChange={(e) => setAppDescription(e.target.value)}
              disabled={isLoading}
            />
          </div>
          
          <div className="flex justify-center">
            <button
              type="submit"
              className={`px-6 py-3 rounded-md text-white font-medium ${
                isLoading
                  ? "bg-gray-500 cursor-not-allowed"
                  : "bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
              }`}
              disabled={isLoading}
            >
              {isLoading ? "Generating App..." : "Generate App"}
            </button>
          </div>
        </form>
      </div>

      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-8 rounded-md" role="alert">
          <p>{error}</p>
        </div>
      )}

      {logs.length > 0 && (
        <div className="bg-gray-100 rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-800 mb-3">Generation Progress</h2>
          <div className="bg-black text-green-400 p-4 rounded-md font-mono text-sm h-64 overflow-y-auto">
            {logs.map((log, index) => (
              <div key={index} className="mb-1">
                &gt; {log}
              </div>
            ))}
          </div>
        </div>
      )}

      {zipUrl && (
        <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-8 rounded-md">
          <h3 className="font-bold mb-2">App Generated Successfully!</h3>
          <p className="mb-4">Your application code is ready to download.</p>
          <a
            href={zipUrl}
            download
            className="inline-block bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-50"
          >
            Download ZIP
          </a>
        </div>
      )}
    </div>
  );
};

function App() {
  return (
    <div className="App min-h-screen bg-gray-100">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
