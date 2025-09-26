import React from 'react';
import { Map, MapPin, Zap, TrendingUp, AlertTriangle, BarChart3 } from 'lucide-react';

const GeospatialDashboard = () => {
  const hotspots = [
    {
      id: 1,
      location: 'Mumbai Metropolitan Area',
      type: 'High Demand Zone',
      riskLevel: 'High',
      projects: 8,
      avgDelay: 45,
      costOverrun: 23,
      coordinates: '19.0760° N, 72.8777° E'
    },
    {
      id: 2,
      location: 'Pune Industrial Belt',
      type: 'Supply Constraint',
      riskLevel: 'Medium',
      projects: 12,
      avgDelay: 28,
      costOverrun: 15,
      coordinates: '18.5204° N, 73.8567° E'
    },
    {
      id: 3,
      location: 'Western Ghats Region',
      type: 'Terrain Challenge',
      riskLevel: 'High',
      projects: 5,
      avgDelay: 62,
      costOverrun: 35,
      coordinates: '16.7050° N, 73.8567° E'
    },
    {
      id: 4,
      location: 'Nashik Agricultural Zone',
      type: 'Seasonal Impact',
      riskLevel: 'Low',
      projects: 6,
      avgDelay: 18,
      costOverrun: 8,
      coordinates: '19.9975° N, 73.7898° E'
    }
  ];

  const regionalStats = [
    { region: 'North Maharashtra', projects: 15, completion: 78, avgCost: 12.5 },
    { region: 'South Maharashtra', projects: 22, completion: 65, avgCost: 18.3 },
    { region: 'West Maharashtra', projects: 18, completion: 82, avgCost: 15.7 },
    { region: 'East Maharashtra', projects: 11, completion: 71, avgCost: 9.8 }
  ];

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'High': return 'bg-red-100 text-red-800 border-red-200';
      case 'Medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'High Demand Zone': return TrendingUp;
      case 'Supply Constraint': return AlertTriangle;
      case 'Terrain Challenge': return Map;
      case 'Seasonal Impact': return BarChart3;
      default: return MapPin;
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Geospatial Hotspot Dashboard</h1>
        <p className="text-gray-600">Analyze regional patterns, risk zones, and project distribution</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Regions</p>
              <p className="text-2xl font-bold text-gray-900">4</p>
            </div>
            <Map className="h-8 w-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">High-Risk Zones</p>
              <p className="text-2xl font-bold text-red-600">2</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-red-600" />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Projects</p>
              <p className="text-2xl font-bold text-blue-600">31</p>
            </div>
            <Zap className="h-8 w-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Completion</p>
              <p className="text-2xl font-bold text-green-600">74%</p>
            </div>
            <TrendingUp className="h-8 w-8 text-green-600" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hotspot Analysis */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Risk Hotspots</h2>
          
          <div className="space-y-4">
            {hotspots.map((hotspot) => {
              const IconComponent = getTypeIcon(hotspot.type);
              return (
                <div key={hotspot.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <IconComponent className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="font-medium text-gray-900">{hotspot.location}</h3>
                        <p className="text-sm text-gray-600">{hotspot.type}</p>
                      </div>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getRiskColor(hotspot.riskLevel)}`}>
                      {hotspot.riskLevel} Risk
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Projects</p>
                      <p className="font-medium text-gray-900">{hotspot.projects}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Avg Delay</p>
                      <p className="font-medium text-orange-600">{hotspot.avgDelay} days</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Cost Overrun</p>
                      <p className="font-medium text-red-600">{hotspot.costOverrun}%</p>
                    </div>
                  </div>
                  
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <p className="text-xs text-gray-500">{hotspot.coordinates}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Regional Performance */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Regional Performance</h2>
          
          <div className="space-y-4">
            {regionalStats.map((region, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-gray-900">{region.region}</h3>
                  <span className="text-sm text-gray-600">{region.projects} projects</span>
                </div>
                
                <div className="space-y-2">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Completion Rate</span>
                      <span className="font-medium">{region.completion}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          region.completion >= 80 ? 'bg-green-600' : 
                          region.completion >= 70 ? 'bg-yellow-600' : 'bg-red-600'
                        }`}
                        style={{ width: `${region.completion}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="flex justify-between text-sm pt-2">
                    <span className="text-gray-600">Avg Project Cost</span>
                    <span className="font-medium text-blue-600">₹{region.avgCost} Cr</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-medium text-blue-900 mb-2">Regional Insights</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• West Maharashtra shows highest completion rates (82%)</li>
              <li>• South Maharashtra has largest project portfolio (22 projects)</li>
              <li>• Eastern regions show lower average project costs</li>
              <li>• Monsoon impact varies significantly by geography</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Map Placeholder */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Interactive Risk Map</h2>
        
        <div className="h-96 bg-gradient-to-br from-blue-50 to-green-50 rounded-lg flex items-center justify-center relative overflow-hidden">
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-12 left-16 w-4 h-4 bg-red-500 rounded-full animate-pulse"></div>
            <div className="absolute top-20 right-20 w-3 h-3 bg-yellow-500 rounded-full"></div>
            <div className="absolute bottom-16 left-12 w-5 h-5 bg-red-500 rounded-full animate-pulse"></div>
            <div className="absolute bottom-20 right-16 w-3 h-3 bg-green-500 rounded-full"></div>
            <div className="absolute top-1/2 left-1/2 w-4 h-4 bg-yellow-500 rounded-full transform -translate-x-1/2 -translate-y-1/2"></div>
          </div>
          
          <div className="text-center z-10">
            <Map className="h-16 w-16 text-blue-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-700 mb-2">Interactive Map View</h3>
            <p className="text-gray-600 max-w-md">
              This area would display an interactive map showing project locations, risk zones, 
              and real-time data overlays for comprehensive geospatial analysis.
            </p>
            <div className="flex items-center justify-center space-x-4 mt-4 text-sm">
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span>High Risk</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <span>Medium Risk</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span>Low Risk</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GeospatialDashboard;