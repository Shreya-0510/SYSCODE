import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Calculator, MessageSquare, Calendar, Map, Zap } from 'lucide-react';

const Navigation = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Cost Prediction', icon: Calculator },
    { path: '/chatbot', label: 'AI Assistant', icon: MessageSquare },
    { path: '/scheduler', label: 'Scheduler', icon: Calendar },
    { path: '/geospatial', label: 'Geospatial Analytics', icon: Map },
  ];

  return (
    <nav className="bg-white shadow-lg border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-2">
            <Zap className="h-8 w-8 text-blue-600" />
            <h1 className="text-xl font-bold text-gray-900">PowerProject Predictor</h1>
          </div>
          
          <div className="flex space-x-1">
            {navItems.map(({ path, label, icon: Icon }) => (
              <Link
                key={path}
                to={path}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  location.pathname === path
                    ? 'bg-blue-100 text-blue-700 border border-blue-200'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span className="font-medium">{label}</span>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;