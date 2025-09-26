"""
Prediction Service for handling ML predictions and business logic
"""

import logging
from datetime import datetime, timedelta
from services.ml_service import MLService
from models.project_model import Project
from models.regional_data import RegionalData

logger = logging.getLogger(__name__)

class PredictionService:
    """
    Service for handling project predictions and analysis
    """
    
    def __init__(self):
        self.ml_service = MLService()
    
    def predict_project_outcomes(self, project_data):
        """
        Predict project outcomes using ML models
        
        Args:
            project_data (dict): Project data dictionary
            
        Returns:
            dict: Prediction results with recommendations
        """
        try:
            # Convert frontend data format to ML format
            ml_features = self._convert_to_ml_format(project_data)
            
            # Get ML predictions
            predictions = self.ml_service.predict(ml_features, prediction_type='all')
            
            # Generate recommendations
            recommendations = self._generate_recommendations(project_data, predictions)
            
            # Calculate risk factors
            risk_factors = self._analyze_risk_factors(project_data, predictions)
            
            # Format response
            result = {
                'predictions': {
                    'cost_overrun_probability': max(0, min(100, predictions.get('cost_overrun_pct', 0))),
                    'predicted_delay_months': max(0, predictions.get('delay_months', 0)),
                    'predicted_total_cost': max(project_data.get('baseEstimatedCost', 0), 
                                              predictions.get('total_cost_cr', 0)),
                    'predicted_timeline_months': max(1, predictions.get('timeline_months', 
                                                   project_data.get('plannedTimelineMonths', 12))),
                    'risk_category': predictions.get('risk_assessment', 'Medium'),
                    'confidence_score': predictions.get('confidence_score', 75)
                },
                'recommendations': recommendations,
                'risk_factors': risk_factors,
                'analysis': {
                    'model_version': '1.0.0',
                    'prediction_date': datetime.utcnow().isoformat(),
                    'data_completeness': self._calculate_data_completeness(project_data)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error predicting project outcomes: {str(e)}")
            # Return fallback predictions
            return self._fallback_predictions(project_data)
    
    def _convert_to_ml_format(self, project_data):
        """Convert frontend project data to ML model format"""
        
        # Map frontend field names to ML model expected names
        field_mapping = {
            'projectType': 'Project_Type',
            'terrainType': 'Terrain', 
            'baseEstimatedCost': 'Base_Cost_Cr',
            'steelPriceIndex': 'Steel_Price_Index',
            'cementPriceIndex': 'Cement_Price_Index',
            'labourWageRate': 'Labour_Wage_RsPerDay',
            'regulatoryDelayEstimate': 'Regulatory_Delay_months',
            'historicalDelayPattern': 'Historical_Delay_Count',
            'annualRainfall': 'Avg_Annual_Rainfall_cm',
            'vendorReliabilityScore': 'Vendor_Reliability',
            'materialAvailabilityIndex': 'Material_Availability_Index',
            'demandSupplyPressure': 'Demand_Supply_Pressure',
            'skilledManpowerAvailability': 'Skilled_Manpower_pct',
            'plannedTimelineMonths': 'Planned_Timeline_months'
        }
        
        ml_features = {}
        
        for frontend_key, ml_key in field_mapping.items():
            if frontend_key in project_data:
                value = project_data[frontend_key]
                
                # Handle special conversions
                if frontend_key == 'projectType':
                    type_mapping = {
                        'substation': 'Substation',
                        'overhead-line': 'Overhead Line',
                        'underground-cable': 'Underground Cable'
                    }
                    ml_features[ml_key] = type_mapping.get(value, 'Substation')
                
                elif frontend_key == 'terrainType':
                    terrain_mapping = {
                        'plains': 'Plains',
                        'hilly': 'Hilly',
                        'desert': 'Desert',
                        'coastal': 'Coastal',
                        'urban': 'Urban',
                        'mountainous': 'Mountainous'
                    }
                    ml_features[ml_key] = terrain_mapping.get(value, 'Plains')
                
                elif frontend_key == 'demandSupplyPressure':
                    pressure_mapping = {
                        'low': 'Low',
                        'medium': 'Medium',
                        'high': 'High'
                    }
                    ml_features[ml_key] = pressure_mapping.get(value, 'Medium')
                
                elif frontend_key == 'historicalDelayPattern':
                    delay_mapping = {'low': 1, 'medium': 3, 'high': 5}
                    ml_features[ml_key] = delay_mapping.get(value, 3)
                
                else:
                    ml_features[ml_key] = value
        
        # Set default values for missing features
        defaults = {
            'Steel_Price_Index': 100,
            'Cement_Price_Index': 100,
            'Regulatory_Delay_months': 0,
            'Historical_Delay_Count': 3,
            'Avg_Annual_Rainfall_cm': 100,
            'Demand_Supply_Pressure': 'Medium',
            'Planned_Timeline_months': 12
        }
        
        for key, default_value in defaults.items():
            if key not in ml_features:
                ml_features[key] = default_value
        
        return ml_features
    
    def _generate_recommendations(self, project_data, predictions):
        """Generate actionable recommendations based on predictions"""
        
        recommendations = []
        
        cost_overrun = predictions.get('cost_overrun_pct', 0)
        delay_months = predictions.get('delay_months', 0)
        risk_level = predictions.get('risk_assessment', 'Medium')
        
        # Cost-related recommendations
        if cost_overrun > 15:
            recommendations.append({
                'type': 'cost',
                'priority': 'high',
                'title': 'High Cost Overrun Risk Detected',
                'description': f'Model predicts {cost_overrun:.1f}% cost overrun. Implement strict cost controls.',
                'actions': [
                    'Negotiate fixed-price contracts with key vendors',
                    'Implement daily cost tracking and reporting',
                    'Consider value engineering to reduce scope',
                    'Increase contingency budget by 20-25%'
                ]
            })
        elif cost_overrun > 8:
            recommendations.append({
                'type': 'cost',
                'priority': 'medium',
                'title': 'Moderate Cost Risk',
                'description': f'Model predicts {cost_overrun:.1f}% cost overrun. Monitor cost trends closely.',
                'actions': [
                    'Weekly cost review meetings',
                    'Lock in material prices where possible',
                    'Monitor vendor performance closely'
                ]
            })
        
        # Timeline-related recommendations
        if delay_months > 4:
            recommendations.append({
                'type': 'timeline',
                'priority': 'high',
                'title': 'Significant Delays Expected',
                'description': f'Model predicts {delay_months:.1f} months delay. Implement acceleration measures.',
                'actions': [
                    'Consider parallel execution of activities',
                    'Engage additional resources for critical path',
                    'Fast-track permitting and approvals',
                    'Implement 24/7 work schedule if feasible'
                ]
            })
        elif delay_months > 2:
            recommendations.append({
                'type': 'timeline',
                'priority': 'medium',
                'title': 'Potential Timeline Risks',
                'description': f'Model predicts {delay_months:.1f} months delay. Optimize scheduling.',
                'actions': [
                    'Review critical path activities',
                    'Improve coordination between teams',
                    'Address resource constraints proactively'
                ]
            })
        
        # Resource-specific recommendations
        vendor_reliability = project_data.get('vendorReliabilityScore', 0.8)
        if vendor_reliability < 0.6:
            recommendations.append({
                'type': 'vendor',
                'priority': 'high',
                'title': 'Vendor Reliability Concerns',
                'description': 'Low vendor reliability score detected. Implement enhanced monitoring.',
                'actions': [
                    'Establish backup vendors for critical items',
                    'Implement vendor performance scorecards',
                    'Increase quality inspection frequency',
                    'Consider vendor development programs'
                ]
            })
        
        material_availability = project_data.get('materialAvailabilityIndex', 0.8)
        if material_availability < 0.7:
            recommendations.append({
                'type': 'materials',
                'priority': 'medium',
                'title': 'Material Availability Risk',
                'description': 'Limited material availability detected. Secure supply chains.',
                'actions': [
                    'Pre-order critical materials',
                    'Identify alternative suppliers',
                    'Consider material substitutions where appropriate',
                    'Implement just-in-time inventory management'
                ]
            })
        
        manpower = project_data.get('skilledManpowerAvailability', 70)
        if manpower < 60:
            recommendations.append({
                'type': 'manpower',
                'priority': 'high',
                'title': 'Skilled Manpower Shortage',
                'description': f'Only {manpower}% skilled manpower available. Address resource gaps.',
                'actions': [
                    'Implement training programs for local workers',
                    'Partner with technical institutes',
                    'Consider bringing in skilled workers from other regions',
                    'Increase automation where possible'
                ]
            })
        
        # Terrain-specific recommendations
        terrain = project_data.get('terrainType', 'plains')
        if terrain in ['mountainous', 'urban']:
            recommendations.append({
                'type': 'terrain',
                'priority': 'medium',
                'title': f'Complex Terrain Challenges ({terrain.title()})',
                'description': 'Complex terrain requires specialized approach and equipment.',
                'actions': [
                    'Engage specialized contractors with terrain experience',
                    'Conduct detailed geological surveys',
                    'Use specialized equipment and techniques',
                    'Allow additional time for logistics'
                ]
            })
        
        # Environmental recommendations
        rainfall = project_data.get('annualRainfall', 100)
        if rainfall > 150:
            recommendations.append({
                'type': 'environmental',
                'priority': 'medium',
                'title': 'High Rainfall Area',
                'description': f'Annual rainfall of {rainfall}cm may cause delays. Plan for weather risks.',
                'actions': [
                    'Schedule outdoor work during dry season',
                    'Invest in weather protection equipment',
                    'Develop monsoon contingency plans',
                    'Consider weather insurance'
                ]
            })
        
        return recommendations
    
    def _analyze_risk_factors(self, project_data, predictions):
        """Analyze and categorize risk factors"""
        
        risk_factors = {
            'financial_risks': [],
            'operational_risks': [],
            'environmental_risks': [],
            'external_risks': []
        }
        
        # Financial risks
        cost_overrun = predictions.get('cost_overrun_pct', 0)
        if cost_overrun > 10:
            risk_factors['financial_risks'].append({
                'factor': 'Cost Overrun Risk',
                'severity': 'High' if cost_overrun > 20 else 'Medium',
                'impact': f'{cost_overrun:.1f}% predicted overrun',
                'mitigation': 'Implement strict cost controls and fixed-price contracts'
            })
        
        steel_price = project_data.get('steelPriceIndex', 100)
        cement_price = project_data.get('cementPriceIndex', 100)
        if abs(steel_price - 100) > 15 or abs(cement_price - 100) > 15:
            risk_factors['financial_risks'].append({
                'factor': 'Material Price Volatility',
                'severity': 'Medium',
                'impact': 'Price fluctuations affecting project costs',
                'mitigation': 'Lock in material prices through forward contracts'
            })
        
        # Operational risks
        vendor_reliability = project_data.get('vendorReliabilityScore', 0.8)
        if vendor_reliability < 0.7:
            risk_factors['operational_risks'].append({
                'factor': 'Vendor Performance Risk',
                'severity': 'High' if vendor_reliability < 0.6 else 'Medium',
                'impact': 'Potential delays due to vendor issues',
                'mitigation': 'Establish backup vendors and performance monitoring'
            })
        
        manpower = project_data.get('skilledManpowerAvailability', 70)
        if manpower < 70:
            risk_factors['operational_risks'].append({
                'factor': 'Skilled Labor Shortage',
                'severity': 'High' if manpower < 50 else 'Medium',
                'impact': f'Only {manpower}% skilled manpower available',
                'mitigation': 'Training programs and alternative sourcing strategies'
            })
        
        # Environmental risks
        terrain = project_data.get('terrainType', 'plains')
        if terrain in ['mountainous', 'urban', 'coastal']:
            severity = 'High' if terrain == 'mountainous' else 'Medium'
            risk_factors['environmental_risks'].append({
                'factor': f'{terrain.title()} Terrain Complexity',
                'severity': severity,
                'impact': 'Increased construction complexity and costs',
                'mitigation': 'Specialized contractors and equipment'
            })
        
        rainfall = project_data.get('annualRainfall', 100)
        if rainfall > 150:
            risk_factors['environmental_risks'].append({
                'factor': 'High Rainfall Impact',
                'severity': 'Medium',
                'impact': f'{rainfall}cm annual rainfall may cause delays',
                'mitigation': 'Weather-based scheduling and protection measures'
            })
        
        # External risks
        regulatory_delay = project_data.get('regulatoryDelayEstimate', 0)
        if regulatory_delay > 3:
            risk_factors['external_risks'].append({
                'factor': 'Regulatory Approval Delays',
                'severity': 'Medium',
                'impact': f'{regulatory_delay} months estimated delays',
                'mitigation': 'Early engagement with regulatory authorities'
            })
        
        demand_pressure = project_data.get('demandSupplyPressure', 'medium')
        if demand_pressure == 'high':
            risk_factors['external_risks'].append({
                'factor': 'Market Demand Pressure',
                'severity': 'Medium',
                'impact': 'Competition for resources and higher costs',
                'mitigation': 'Early resource booking and strategic partnerships'
            })
        
        return risk_factors
    
    def _calculate_data_completeness(self, project_data):
        """Calculate completeness score of input data"""
        
        required_fields = [
            'projectType', 'terrainType', 'baseEstimatedCost', 'labourWageRate',
            'vendorReliabilityScore', 'materialAvailabilityIndex', 'skilledManpowerAvailability'
        ]
        
        optional_fields = [
            'steelPriceIndex', 'cementPriceIndex', 'regulatoryDelayEstimate',
            'annualRainfall', 'demandSupplyPressure', 'historicalDelayPattern'
        ]
        
        required_score = sum(1 for field in required_fields if field in project_data and project_data[field] is not None)
        optional_score = sum(1 for field in optional_fields if field in project_data and project_data[field] is not None)
        
        total_score = (required_score * 2 + optional_score) / (len(required_fields) * 2 + len(optional_fields)) * 100
        
        return round(total_score, 1)
    
    def _fallback_predictions(self, project_data):
        """Provide fallback predictions when ML models fail"""
        
        logger.warning("Using fallback prediction logic")
        
        # Simple rule-based predictions
        base_cost = project_data.get('baseEstimatedCost', 1000)
        terrain = project_data.get('terrainType', 'plains')
        vendor_reliability = project_data.get('vendorReliabilityScore', 0.8)
        
        # Terrain multipliers
        terrain_multipliers = {
            'plains': 1.0,
            'hilly': 1.15,
            'desert': 1.10,
            'coastal': 1.20,
            'urban': 1.25,
            'mountainous': 1.35
        }
        
        terrain_factor = terrain_multipliers.get(terrain, 1.0)
        vendor_factor = 2.0 - vendor_reliability  # Inverted reliability
        
        # Calculate fallback predictions
        cost_overrun = max(0, min(50, (terrain_factor - 1) * 100 + (vendor_factor - 1) * 25))
        delay_months = max(0, (terrain_factor - 1) * 12 + (vendor_factor - 1) * 6)
        
        risk = 'High' if cost_overrun > 20 or delay_months > 4 else 'Medium' if cost_overrun > 10 or delay_months > 2 else 'Low'
        
        return {
            'predictions': {
                'cost_overrun_probability': round(cost_overrun, 1),
                'predicted_delay_months': round(delay_months, 1),
                'predicted_total_cost': base_cost * (1 + cost_overrun / 100),
                'predicted_timeline_months': project_data.get('plannedTimelineMonths', 12) + delay_months,
                'risk_category': risk,
                'confidence_score': 60.0  # Lower confidence for fallback
            },
            'recommendations': [],
            'risk_factors': {'financial_risks': [], 'operational_risks': [], 'environmental_risks': [], 'external_risks': []},
            'analysis': {
                'model_version': 'fallback-1.0',
                'prediction_date': datetime.utcnow().isoformat(),
                'data_completeness': self._calculate_data_completeness(project_data),
                'note': 'Using fallback prediction logic'
            }
        }
    
    def bulk_predict_projects(self, project_ids):
        """Predict outcomes for multiple existing projects"""
        
        try:
            results = {}
            
            for project_id in project_ids:
                project = Project.query.filter_by(project_id=project_id).first()
                
                if project:
                    # Convert project to prediction format
                    project_data = self._project_to_prediction_format(project)
                    
                    # Get predictions
                    predictions = self.predict_project_outcomes(project_data)
                    
                    # Store predictions in project
                    project.set_predictions(predictions['predictions'])
                    project.risk = predictions['predictions']['risk_category']
                    
                    results[project_id] = predictions
                    
                else:
                    results[project_id] = {'error': 'Project not found'}
            
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk prediction: {str(e)}")
            raise
    
    def _project_to_prediction_format(self, project):
        """Convert Project model to prediction input format"""
        
        return {
            'projectType': project.project_type.lower().replace(' ', '-') if project.project_type else 'substation',
            'terrainType': project.terrain.lower() if project.terrain else 'plains',
            'baseEstimatedCost': project.base_cost_cr or 1000,
            'steelPriceIndex': project.steel_price_index or 100,
            'cementPriceIndex': project.cement_price_index or 100,
            'labourWageRate': project.labour_wage_rs_per_day or 400,
            'vendorReliabilityScore': project.vendor_reliability or 0.8,
            'materialAvailabilityIndex': project.material_availability_index or 0.8,
            'skilledManpowerAvailability': project.skilled_manpower_pct or 70,
            'regulatoryDelayEstimate': project.regulatory_delay_months or 0,
            'annualRainfall': project.avg_annual_rainfall_cm or 100,
            'demandSupplyPressure': project.demand_supply_pressure.lower() if project.demand_supply_pressure else 'medium',
            'historicalDelayPattern': 'medium',  # Default
            'plannedTimelineMonths': project.planned_timeline_months or 12
        }
    
    def update_project_with_predictions(self, project_id, predictions_data):
        """Update a project with prediction results"""
        
        try:
            project = Project.query.filter_by(project_id=project_id).first()
            
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            # Store predictions
            project.set_predictions(predictions_data['predictions'])
            project.risk = predictions_data['predictions']['risk_category']
            
            # Update calculated overrun if we have actual costs
            if project.total_cost_cr:
                project.overrun_pct = project.calculate_cost_overrun_pct()
            
            # Save to database
            from app import db
            db.session.commit()
            
            logger.info(f"Updated project {project_id} with predictions")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating project with predictions: {str(e)}")
            raise