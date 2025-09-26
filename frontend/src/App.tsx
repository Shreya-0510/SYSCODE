import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import PredictionForm from './components/PredictionForm';
import ChatbotPage from './components/ChatbotPage';
import SchedulerDashboard from './components/SchedulerDashboard';
import GeospatialDashboard from './components/GeospatialDashboard';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<PredictionForm />} />
            <Route path="/chatbot" element={<ChatbotPage />} />
            <Route path="/scheduler" element={<SchedulerDashboard />} />
            <Route path="/geospatial" element={<GeospatialDashboard />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;