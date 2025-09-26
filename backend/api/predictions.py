"""
API endpoints for ML predictions
"""

from flask import request, jsonify
from flask_restful import Resource
import logging
from services.prediction_service import PredictionService
from services.ml_service import MLService
from services.team_ml_service import TeamMLService

logger = logging.getLogger(__name__)

class PredictionResource(Resource):
    """
    Resource for handling individual prediction requests
    """
    
    def __init__(self):
        self.prediction_service = PredictionService()
    
    def post(self):
        """
        Calculate predictions for project data
        
        Expected JSON format:
        {
            "projectType": "substation",
            "terrainType": "urban", 
            "location": "Maharashtra/Mumbai",
            "baseEstimatedCost": 1200.0,
            "labourWageRate": 450.0,
            "steelPriceIndex": 105.0,
            "cementPriceIndex": 110.0,
            "vendorReliabilityScore": 0.8,
            "materialAvailabilityIndex": 0.75,
            "skilledManpowerAvailability": 70,
            "regulatoryDelayEstimate": 2.0,
            "historicalDelayPattern": "medium",
            "annualRainfall": 120.0,
            "demandSupplyPressure": "high",
            "plannedTimelineMonths": 24
        }
        """
        try:
            # Validate request
            if not request.json:
                return {
                    'success': False,
                    'message': 'No JSON data provided'
                }, 400
            
            project_data = request.json
            
            # Validate required fields
            required_fields = [
                'projectType', 'terrainType', 'baseEstimatedCost', 
                'labourWageRate', 'vendorReliabilityScore', 'materialAvailabilityIndex',
                'skilledManpowerAvailability'
            ]
            
            missing_fields = [field for field in required_fields if field not in project_data]
            if missing_fields:
                return {
                    'success': False,
                    'message': f'Missing required fields: {", ".join(missing_fields)}'
                }, 400
            
            # Get predictions
            predictions = self.prediction_service.predict_project_outcomes(project_data)
            
            return {
                'success': True,
                'data': predictions
            }, 200
            
        except ValueError as e:
            logger.warning(f"Validation error in prediction: {str(e)}")
            return {
                'success': False,
                'message': f'Validation error: {str(e)}'
            }, 400
            
        except Exception as e:
            logger.error(f"Error in prediction endpoint: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error during prediction'
            }, 500


class BatchPredictionResource(Resource):
    """
    Resource for handling batch prediction requests
    """
    
    def __init__(self):
        self.prediction_service = PredictionService()
    
    def post(self):
        """
        Calculate predictions for multiple projects
        
        Expected JSON format:
        {
            "project_ids": ["PG4001", "PG4002", "PG4003"]
        }
        """
        try:
            if not request.json or 'project_ids' not in request.json:
                return {
                    'success': False,
                    'message': 'project_ids array is required'
                }, 400
            
            project_ids = request.json['project_ids']
            
            if not isinstance(project_ids, list) or not project_ids:
                return {
                    'success': False,
                    'message': 'project_ids must be a non-empty array'
                }, 400
            
            # Get batch predictions
            results = self.prediction_service.bulk_predict_projects(project_ids)
            
            # Separate successful and failed predictions
            successful = {}
            failed = {}
            
            for project_id, result in results.items():
                if 'error' in result:
                    failed[project_id] = result
                else:
                    successful[project_id] = result
            
            return {
                'success': True,
                'data': {
                    'successful_predictions': successful,
                    'failed_predictions': failed,
                    'summary': {
                        'total_requested': len(project_ids),
                        'successful_count': len(successful),
                        'failed_count': len(failed)
                    }
                }
            }, 200
            
        except Exception as e:
            logger.error(f"Error in batch prediction endpoint: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error during batch prediction'
            }, 500
    
    def get(self):
        """
        Get recent prediction results and statistics
        """
        try:
            from models.project_model import Project
            from app import db
            
            # Get projects with recent predictions
            recent_projects = Project.query.filter(
                Project.last_prediction_date.isnot(None)
            ).order_by(Project.last_prediction_date.desc()).limit(50).all()
            
            # Calculate statistics
            if recent_projects:
                predictions_data = []
                high_risk_count = 0
                medium_risk_count = 0
                low_risk_count = 0
                
                total_cost_overrun = 0
                total_delay = 0
                confidence_scores = []
                
                for project in recent_projects:
                    pred_data = project.get_predictions()
                    if pred_data:
                        predictions_data.append({
                            'project_id': project.project_id,
                            'name': project.name,
                            'predictions': pred_data,
                            'risk': project.risk,
                            'prediction_date': project.last_prediction_date.isoformat() if project.last_prediction_date else None
                        })
                        
                        # Count risk levels
                        if project.risk == 'High':
                            high_risk_count += 1
                        elif project.risk == 'Medium':
                            medium_risk_count += 1
                        else:
                            low_risk_count += 1
                        
                        # Aggregate metrics
                        if 'cost_overrun_probability' in pred_data:
                            total_cost_overrun += pred_data['cost_overrun_probability']
                        
                        if 'predicted_delay_months' in pred_data:
                            total_delay += pred_data['predicted_delay_months']
                        
                        if 'confidence_score' in pred_data:
                            confidence_scores.append(pred_data['confidence_score'])
                
                # Calculate averages
                avg_cost_overrun = total_cost_overrun / len(recent_projects) if recent_projects else 0
                avg_delay = total_delay / len(recent_projects) if recent_projects else 0
                avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
                
                statistics = {
                    'total_projects_with_predictions': len(recent_projects),
                    'risk_distribution': {
                        'high_risk': high_risk_count,
                        'medium_risk': medium_risk_count,
                        'low_risk': low_risk_count
                    },
                    'average_metrics': {
                        'cost_overrun_probability': round(avg_cost_overrun, 2),
                        'predicted_delay_months': round(avg_delay, 2),
                        'confidence_score': round(avg_confidence, 2)
                    }
                }
                
                return {
                    'success': True,
                    'data': {
                        'recent_predictions': predictions_data[:20],  # Limit to 20 for response size
                        'statistics': statistics
                    }
                }, 200
            
            else:
                return {
                    'success': True,
                    'data': {
                        'recent_predictions': [],
                        'statistics': {
                            'total_projects_with_predictions': 0,
                            'risk_distribution': {'high_risk': 0, 'medium_risk': 0, 'low_risk': 0},
                            'average_metrics': {'cost_overrun_probability': 0, 'predicted_delay_months': 0, 'confidence_score': 0}
                        }
                    }
                }, 200
                
        except Exception as e:
            logger.error(f"Error getting batch prediction data: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500


class ComprehensivePredictionResource(Resource):
    """
    Resource for comprehensive predictions using production ML pipelines
    """
    
    def __init__(self):
        self.ml_service = MLService()
    
    def post(self):
        """
        Simple prediction using your 3 trained models
        """
        try:
            if not request.json:
                return {'success': False, 'message': 'No data provided'}, 400
            
            project_data = request.json
            
            # Make prediction with your models
            predictions = self.ml_service.predict(project_data, prediction_type='all')
            
            return {
                'success': True,
                'predictions': predictions,
                'message': 'Predictions completed using your trained models'
            }, 200
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }, 500


class ModelInfoResource(Resource):
    """
    Resource for getting ML model information and performance
    """
    
    def __init__(self):
        self.ml_service = MLService()
    
    def get(self):
        """
        Get information about loaded ML models
        """
        try:
            model_info = {
                'models_loaded': self.ml_service.models_loaded,
                'available_models': list(self.ml_service.model_configs.keys()),
                'feature_columns': self.ml_service.feature_columns if self.ml_service.feature_columns else [],
                'target_columns': self.ml_service.target_columns
            }
            
            # Get feature importance if models are loaded
            if self.ml_service.models_loaded:
                feature_importance = {}
                for model_name in self.ml_service.model_configs:
                    if model_name in self.ml_service.models:
                        importance = self.ml_service.get_feature_importance(model_name)
                        if importance:
                            # Get top 10 features
                            feature_importance[model_name] = dict(list(importance.items())[:10])
                
                model_info['feature_importance'] = feature_importance
            
            return {
                'success': True,
                'data': model_info
            }, 200
            
        except Exception as e:
            logger.error(f"Error getting model info: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500


class RetrainModelResource(Resource):
    """
    Resource for retraining ML models
    """
    
    def __init__(self):
        self.ml_service = MLService()
    
    def post(self):
        """
        Retrain a specific model or all models
        
        Expected JSON format:
        {
            "model_name": "cost_overrun",  # Optional, if not provided, retrain all
            "dataset_path": "/path/to/new/data.csv"  # Optional, use default if not provided
        }
        """
        try:
            data = request.json or {}
            model_name = data.get('model_name')
            dataset_path = data.get('dataset_path')
            
            if model_name:
                # Retrain specific model
                if model_name not in self.ml_service.model_configs:
                    return {
                        'success': False,
                        'message': f'Unknown model name: {model_name}'
                    }, 400
                
                success = self.ml_service.retrain_model(model_name, dataset_path)
                
                return {
                    'success': success,
                    'message': f'Model {model_name} retrained successfully' if success else 'Retraining failed'
                }, 200 if success else 500
            
            else:
                # Retrain all models
                from app import app
                dataset_path = dataset_path or app.config['DATASET_PATH']
                
                success = self.ml_service.train_models(dataset_path, save_models=True)
                
                return {
                    'success': success,
                    'message': 'All models retrained successfully' if success else 'Retraining failed'
                }, 200 if success else 500
                
        except Exception as e:
            logger.error(f"Error retraining models: {str(e)}")
            return {
                'success': False,
                'message': f'Error during retraining: {str(e)}'
            }, 500