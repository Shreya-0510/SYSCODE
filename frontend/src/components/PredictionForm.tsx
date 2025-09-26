import React, { useState } from 'react';
import { TrendingUp, AlertTriangle, CheckCircle, Loader2 } from 'lucide-react';

interface FormData {
  projectId: string;
  projectType: string;
  location: string;
  terrainType: string;
  baseEstimatedCost: number;
  labourWageRate: number;
  steelPriceIndex: number;
  cementPriceIndex: number;
  vendorReliabilityScore: number;
  materialAvailabilityIndex: number;
  regulatoryDelayEstimate: number;
  historicalDelayPattern: string;
  annualRainfall: number;
  demandSupplyPressure: string;
  skilledManpowerAvailability: number;
}

interface PredictionResponse {
  costOverrunProbability: number;
  predictedDelay: number;
  riskCategory: string;
  predictedCost?: number;
  confidence?: number;
}

// Custom numeric input component that handles both manual input and spinner controls
const NumericInput = ({ 
  value, 
  onChange, 
  placeholder = "", 
  step = "1", 
  min,
  max,
  className = "",
  ...props 
}: {
  value: number;
  onChange: (value: number) => void;
  placeholder?: string;
  step?: string;
  min?: number;
  max?: number;
  className?: string;
  [key: string]: any;
}) => {
  const [displayValue, setDisplayValue] = useState(value.toString());

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setDisplayValue(newValue);
    
    // Parse and validate the value
    const numericValue = parseFloat(newValue);
    if (!isNaN(numericValue)) {
      onChange(numericValue);
    } else if (newValue === "" || newValue === "-") {
      // Allow empty string and negative sign for better UX
      onChange(0);
    }
  };

  const handleBlur = () => {
    // Clean up the display value when input loses focus
    const numericValue = parseFloat(displayValue);
    if (!isNaN(numericValue)) {
      setDisplayValue(numericValue.toString());
    } else {
      setDisplayValue("0");
      onChange(0);
    }
  };

  // Update display value when prop changes (but preserve user input while typing)
  React.useEffect(() => {
    if (document.activeElement !== document.querySelector(`input[value="${displayValue}"]`)) {
      setDisplayValue(value.toString());
    }
  }, [value]);

  return (
    <input
      type="number"
      value={displayValue}
      onChange={handleInputChange}
      onBlur={handleBlur}
      placeholder={placeholder}
      step={step}
      min={min}
      max={max}
      className={`w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${className}`}
      {...props}
    />
  );
};

const PredictionForm = () => {
  const [formData, setFormData] = useState<FormData>({
    projectId: '',
    projectType: '',
    location: '',
    terrainType: '',
    baseEstimatedCost: 0,
    labourWageRate: 0,
    steelPriceIndex: 100,
    cementPriceIndex: 100,
    vendorReliabilityScore: 0.8,
    materialAvailabilityIndex: 0.8,
    regulatoryDelayEstimate: 0,
    historicalDelayPattern: 'medium',
    annualRainfall: 0,
    demandSupplyPressure: 'medium',
    skilledManpowerAvailability: 80,
  });

  const [predictions, setPredictions] = useState<PredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (field: keyof FormData, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const generateProjectId = () => {
    const id = 'PRJ-' + Date.now().toString().slice(-6);
    setFormData(prev => ({ ...prev, projectId: id }));
  };

  const calculatePredictions = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // If no projectId, generate one
      const projectId = formData.projectId || 'PRJ-' + Date.now().toString().slice(-6);
      
      // Prepare the data for your backend API
      const requestData = {
        projectType: formData.projectType || 'Overhead Line',
        state: 'Maharashtra', // You can make this dynamic later
        terrain: 'Plains', // You can make this dynamic later  
        baseCost: Number(formData.baseEstimatedCost) || 100,
        plannedTimeline: 24, // You can make this dynamic later
        steelPrice: Number(formData.steelPriceIndex) || 100,
        cementPrice: Number(formData.cementPriceIndex) || 100,
        labourWage: Number(formData.labourWageRate) || 500,
        regulatoryDelay: Number(formData.regulatoryDelayEstimate) || 2,
        historicalDelay: 1, // You can make this dynamic later
        rainfall: Number(formData.annualRainfall) || 120,
        vendorReliability: Number(formData.vendorReliabilityScore) / 100 || 0.8, // Convert to decimal
        materialAvailability: Number(formData.materialAvailabilityIndex) / 100 || 0.8, // Convert to decimal
        demandSupplyPressure: 'Medium', // Convert from High/Low/Medium
        skilledManpower: Number(formData.skilledManpowerAvailability) || 70,
        delayMonths: 0,
        envRisk: 0.3,
        latitude: 19.0760, // Default Mumbai coordinates
        longitude: 72.8777
      };

      // Call your backend API for comprehensive predictions
      const response = await fetch('http://localhost:5000/api/predictions/comprehensive', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        throw new Error(`API call failed: ${response.statusText}`);
      }

      const result = await response.json();
      
      if (result.success) {
        // Extract prediction data from your ML models
        const predictions = result.predictions;
        
        setPredictions({
          costOverrunProbability: predictions.overrun_prediction || 0,
          predictedDelay: predictions.timeline_prediction || 0,
          riskCategory: 'Medium', // You can enhance this based on predictions
          predictedCost: predictions.cost_prediction || formData.baseEstimatedCost,
          confidence: 0.85 // You can use result.confidence_score if available
        });
        
        // Update projectId if it was generated
        if (!formData.projectId) {
          setFormData(prev => ({ ...prev, projectId }));
        }
      } else {
        throw new Error(result.error || 'Prediction failed');
      }
      
    } catch (err) {
      console.error('Error calling prediction API:', err);
      setError(err instanceof Error ? err.message : 'Failed to get predictions. Using fallback calculation.');
      
      // Fallback to local calculation if API fails
      calculateFallbackPredictions();
    } finally {
      setIsLoading(false);
    }
  };

  const calculateFallbackPredictions = () => {
    // Fallback calculation logic (same as before) for when API is unavailable
    const terrainMultiplier = {
      'plains': 1.0,
      'hilly': 1.2,
      'desert': 1.15,
      'coastal': 1.25,
      'urban': 1.3,
      'mountainous': 1.4
    }[formData.terrainType] || 1.0;

    const delayPatternMultiplier = {
      'low': 0.8,
      'medium': 1.0,
      'high': 1.3
    }[formData.historicalDelayPattern] || 1.0;

    const demandPressureMultiplier = {
      'low': 0.9,
      'medium': 1.0,
      'high': 1.2
    }[formData.demandSupplyPressure] || 1.0;

    const baseOverrunRisk = 25;
    const costOverrunProbability = Math.min(95, Math.max(5, 
      baseOverrunRisk * 
      terrainMultiplier * 
      delayPatternMultiplier * 
      demandPressureMultiplier * 
      (2 - formData.vendorReliabilityScore) * 
      (2 - formData.materialAvailabilityIndex) * 
      (formData.steelPriceIndex / 100) * 
      (formData.cementPriceIndex / 100) * 
      (120 - formData.skilledManpowerAvailability) / 100
    ));

    const baseDays = 30;
    const predictedDelay = Math.max(0, Math.round(
      baseDays * terrainMultiplier * delayPatternMultiplier * 
      (formData.regulatoryDelayEstimate * 30 / 365) + 
      (formData.annualRainfall > 150 ? 15 : 0) +
      ((100 - formData.skilledManpowerAvailability) / 5)
    ));

    let riskCategory = 'Low';
    if (costOverrunProbability > 60 || predictedDelay > 90) {
      riskCategory = 'High';
    } else if (costOverrunProbability > 35 || predictedDelay > 45) {
      riskCategory = 'Medium';
    }

    setPredictions({
      costOverrunProbability: Math.round(costOverrunProbability),
      predictedDelay,
      riskCategory,
      predictedCost: formData.baseEstimatedCost * (1 + costOverrunProbability / 100),
      confidence: 0.7 // Lower confidence for fallback calculation
    });
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'Low': return 'text-green-700 bg-green-100 border-green-200';
      case 'Medium': return 'text-yellow-700 bg-yellow-100 border-yellow-200';
      case 'High': return 'text-red-700 bg-red-100 border-red-200';
      default: return 'text-gray-700 bg-gray-100 border-gray-200';
    }
  };

  const getRiskIcon = (risk: string) => {
    switch (risk) {
      case 'Low': return CheckCircle;
      case 'Medium': return TrendingUp;
      case 'High': return AlertTriangle;
      default: return TrendingUp;
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Project Cost & Timeline Prediction</h1>
        <p className="text-gray-600">Analyze project risks and predict cost overruns with AI-powered insights</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form Section */}
        <div className="lg:col-span-2 space-y-6">
          {/* Project Details */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <div className="w-2 h-6 bg-blue-600 rounded-full mr-3"></div>
              Project Details
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Project ID
                </label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={formData.projectId}
                    onChange={(e) => handleInputChange('projectId', e.target.value)}
                    placeholder="Auto-generated if blank"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  <button
                    onClick={generateProjectId}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    Generate
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Project Type
                </label>
                <select
                  value={formData.projectType}
                  onChange={(e) => handleInputChange('projectType', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select project type</option>
                  <option value="substation">Substation</option>
                  <option value="overhead-line">Overhead Line</option>
                  <option value="underground-cable">Underground Cable</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Location (State/District)
                </label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => handleInputChange('location', e.target.value)}
                  placeholder="e.g., Maharashtra/Mumbai"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Terrain Type
                </label>
                <select
                  value={formData.terrainType}
                  onChange={(e) => handleInputChange('terrainType', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select terrain</option>
                  <option value="plains">Plains</option>
                  <option value="hilly">Hilly</option>
                  <option value="desert">Desert</option>
                  <option value="coastal">Coastal</option>
                  <option value="urban">Urban</option>
                  <option value="mountainous">Mountainous</option>
                </select>
              </div>
            </div>
          </div>

          {/* Cost & Resource Inputs */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <div className="w-2 h-6 bg-green-600 rounded-full mr-3"></div>
              Cost & Resource Inputs
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Base Estimated Cost (₹ Cr)
                </label>
                <NumericInput
                  value={formData.baseEstimatedCost}
                  onChange={(value) => handleInputChange('baseEstimatedCost', value)}
                  step="0.1"
                  min={0}
                  placeholder="e.g., 100.5"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Labour Wage Rate (₹/day)
                </label>
                <NumericInput
                  value={formData.labourWageRate}
                  onChange={(value) => handleInputChange('labourWageRate', value)}
                  min={0}
                  placeholder="e.g., 500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Steel Price Index
                </label>
                <NumericInput
                  value={formData.steelPriceIndex}
                  onChange={(value) => handleInputChange('steelPriceIndex', value)}
                  step="0.1"
                  min={0}
                  placeholder="e.g., 100"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Cement Price Index
                </label>
                <NumericInput
                  value={formData.cementPriceIndex}
                  onChange={(value) => handleInputChange('cementPriceIndex', value)}
                  step="0.1"
                  min={0}
                  placeholder="e.g., 100"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Vendor Reliability Score: {formData.vendorReliabilityScore.toFixed(2)}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={formData.vendorReliabilityScore}
                  onChange={(e) => handleInputChange('vendorReliabilityScore', parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>0.0 (Poor)</span>
                  <span>1.0 (Excellent)</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Material Availability Index: {formData.materialAvailabilityIndex.toFixed(2)}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={formData.materialAvailabilityIndex}
                  onChange={(e) => handleInputChange('materialAvailabilityIndex', parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>0.0 (Scarce)</span>
                  <span>1.0 (Abundant)</span>
                </div>
              </div>
            </div>
          </div>

          {/* Delays & Environment */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <div className="w-2 h-6 bg-orange-600 rounded-full mr-3"></div>
              Delays & Environment
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Regulatory Delay Estimate (months)
                </label>
                <NumericInput
                  value={formData.regulatoryDelayEstimate}
                  onChange={(value) => handleInputChange('regulatoryDelayEstimate', value)}
                  step="0.1"
                  min={0}
                  placeholder="e.g., 6"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Historical Delay Pattern
                </label>
                <select
                  value={formData.historicalDelayPattern}
                  onChange={(e) => handleInputChange('historicalDelayPattern', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Annual Rainfall (cm)
                </label>
                <NumericInput
                  value={formData.annualRainfall}
                  onChange={(value) => handleInputChange('annualRainfall', value)}
                  step="0.1"
                  min={0}
                  placeholder="e.g., 120.5"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Demand-Supply Pressure
                </label>
                <select
                  value={formData.demandSupplyPressure}
                  onChange={(e) => handleInputChange('demandSupplyPressure', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Skilled Manpower Availability: {formData.skilledManpowerAvailability}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="1"
                  value={formData.skilledManpowerAvailability}
                  onChange={(e) => handleInputChange('skilledManpowerAvailability', parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>0% (Critical Shortage)</span>
                  <span>100% (Fully Available)</span>
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={calculatePredictions}
            disabled={isLoading}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed transition-colors font-medium text-lg flex items-center justify-center"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Calculating...
              </>
            ) : (
              'Calculate Predictions'
            )}
          </button>
        </div>

        {/* Results Section */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 sticky top-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Prediction Results</h2>
            
            {error && (
              <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-yellow-800 text-sm">
                  <AlertTriangle className="w-4 h-4 inline mr-1" />
                  {error}
                </p>
              </div>
            )}
            
            {predictions ? (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-red-50 rounded-lg">
                    <div className="text-3xl font-bold text-red-600 mb-1">
                      {predictions.costOverrunProbability}%
                    </div>
                    <div className="text-sm font-medium text-gray-600">
                      Cost Overrun Risk
                    </div>
                  </div>

                  <div className="text-center p-4 bg-orange-50 rounded-lg">
                    <div className="text-3xl font-bold text-orange-600 mb-1">
                      {predictions.predictedDelay}
                    </div>
                    <div className="text-sm font-medium text-gray-600">
                      Predicted Delay (days)
                    </div>
                  </div>

                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-3xl font-bold text-blue-600 mb-1">
                      ₹{predictions.predictedCost ? predictions.predictedCost.toFixed(1) : formData.baseEstimatedCost.toFixed(1)} Cr
                    </div>
                    <div className="text-sm font-medium text-gray-600">
                      Predicted Final Cost
                    </div>
                  </div>
                </div>

                <div className="text-center">
                  <div className={`inline-flex items-center space-x-2 px-4 py-2 rounded-lg border font-medium ${getRiskColor(predictions.riskCategory)}`}>
                    {React.createElement(getRiskIcon(predictions.riskCategory), { className: "h-5 w-5" })}
                    <span>{predictions.riskCategory} Risk</span>
                  </div>
                </div>

                {predictions.confidence && (
                  <div className="text-center">
                    <div className="text-sm text-gray-600">
                      Prediction Confidence: <span className="font-medium">{Math.round(predictions.confidence * 100)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                        style={{ width: `${predictions.confidence * 100}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                <div className="pt-4 border-t border-gray-200">
                  <h3 className="font-medium text-gray-900 mb-2">Project Summary</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Project Type:</span>
                      <span className="font-medium">{formData.projectType || 'Not specified'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Location:</span>
                      <span className="font-medium">{formData.location || 'Not specified'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Terrain:</span>
                      <span className="font-medium">{formData.terrainType || 'Not specified'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Vendor Reliability:</span>
                      <span className="font-medium">{(formData.vendorReliabilityScore * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Material Availability:</span>
                      <span className="font-medium">{(formData.materialAvailabilityIndex * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Skilled Manpower:</span>
                      <span className="font-medium">{formData.skilledManpowerAvailability}%</span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">
                <TrendingUp className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>Fill out the form and click "Calculate Predictions" to see results</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PredictionForm;