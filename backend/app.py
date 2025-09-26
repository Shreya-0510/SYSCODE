"""
Flask ML Backend for Powergrid Project Management System
Main application fil    from api.predictions import PredictionResource, BatchPredictionResource, ComprehensivePredictionResource, ModelInfoResource, RetrainModelResource
    api.add_resource(PredictionResource, '/api/predictions/calculate')
    api.add_resource(BatchPredictionResource, '/api/predictions/batch')
    api.add_resource(ComprehensivePredictionResource, '/api/predictions/comprehensive')
    api.add_resource(ModelInfoResource, '/api/predictions/model-info')
    api.add_resource(RetrainModelResource, '/api/predictions/retrain')h ML integration and comprehensive API endpoints
"""

import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from dotenv import load_dotenv
import warnings
from datetime import datetime

# Suppress warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///powergrid.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO', 'False').lower() == 'true'
    
    # ML Model Configuration
    MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models', 'trained_models')
    DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'powergrid_projects_300rows.csv')
    
    # API Configuration
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT', '100/hour')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')

app.config.from_object(Config)

# Initialize database
from database import init_database, db
init_database(app)

# Import models after database is initialized
from models.project_model import Project
from models.regional_data import RegionalData
from models.analytics import Analytics

# Initialize API
api = Api(app)

# Enable CORS
CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import ML services
ml_service = None
prediction_service = None

try:
    from services.ml_service import MLService
    from services.prediction_service import PredictionService
    ml_service = MLService()
    prediction_service = PredictionService()
    logger.info("ML services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize ML services: {str(e)}")

# Import and register all API resources
try:
    # Prediction endpoints
    from api.predictions import PredictionResource, BatchPredictionResource, ModelInfoResource, RetrainModelResource
    api.add_resource(PredictionResource, '/api/predictions/calculate')
    api.add_resource(BatchPredictionResource, '/api/predictions/batch')
    api.add_resource(ModelInfoResource, '/api/predictions/models')
    api.add_resource(RetrainModelResource, '/api/predictions/retrain')

    # Project endpoints
    from api.projects import ProjectResource, ProjectStatsResource, ProjectSearchResource
    api.add_resource(ProjectResource, 
                    '/api/projects',  # GET all projects, POST new project
                    '/api/projects/<string:project_id>')  # GET, PUT, DELETE specific project
    api.add_resource(ProjectStatsResource, '/api/projects/stats')
    api.add_resource(ProjectSearchResource, '/api/projects/search')

    # Analytics endpoints
    from api.analytics import AnalyticsResource, AnalyticsExportResource
    api.add_resource(AnalyticsResource, 
                    '/api/analytics',  # GET comprehensive analytics
                    '/api/analytics/<string:analytics_type>')  # GET specific analytics type
    api.add_resource(AnalyticsExportResource, '/api/analytics/export')

    # Chatbot endpoints
    from api.chatbot import ChatbotResource, ChatbotStatsResource
    api.add_resource(ChatbotResource, '/api/chatbot')
    api.add_resource(ChatbotStatsResource, '/api/chatbot/stats')

    # Scheduler endpoints
    from api.scheduler import SchedulerResource, SchedulerStatsResource, TaskResource
    api.add_resource(SchedulerResource, 
                    '/api/scheduler',  # GET comprehensive schedule, POST new task
                    '/api/scheduler/<string:schedule_type>')  # GET specific schedule type
    api.add_resource(SchedulerStatsResource, '/api/scheduler/stats')
    api.add_resource(TaskResource, '/api/scheduler/tasks/<string:task_id>')

    # Geospatial endpoints
    from api.geospatial import GeospatialResource, GeospatialSearchResource, GeospatialExportResource
    api.add_resource(GeospatialResource, 
                    '/api/geospatial',  # GET comprehensive geospatial data
                    '/api/geospatial/<string:data_type>')  # GET specific data type
    api.add_resource(GeospatialSearchResource, '/api/geospatial/search')
    api.add_resource(GeospatialExportResource, '/api/geospatial/export')
    
    logger.info("All API endpoints registered successfully")

except Exception as e:
    logger.error(f"Error registering API endpoints: {str(e)}")

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        'message': 'PowerGrid ML Backend API',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'active',
        'api_endpoints': {
            'predictions': {
                'calculate': '/api/predictions/calculate',
                'batch': '/api/predictions/batch',
                'models': '/api/predictions/models',
                'retrain': '/api/predictions/retrain'
            },
            'projects': {
                'list': '/api/projects',
                'detail': '/api/projects/<project_id>',
                'stats': '/api/projects/stats',
                'search': '/api/projects/search'
            },
            'analytics': {
                'dashboard': '/api/analytics',
                'specific': '/api/analytics/<analytics_type>',
                'export': '/api/analytics/export'
            },
            'chatbot': {
                'message': '/api/chatbot',
                'stats': '/api/chatbot/stats'
            },
            'scheduler': {
                'dashboard': '/api/scheduler',
                'specific': '/api/scheduler/<schedule_type>',
                'stats': '/api/scheduler/stats',
                'tasks': '/api/scheduler/tasks/<task_id>'
            },
            'geospatial': {
                'dashboard': '/api/geospatial',
                'specific': '/api/geospatial/<data_type>',
                'search': '/api/geospatial/search',
                'export': '/api/geospatial/export'
            }
        }
    })

# Health check endpoint
@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        db_status = 'connected'
        
        # Get database stats
        project_count = Project.query.count() if Project else 0
        
    except Exception as e:
        db_status = f'error: {str(e)}'
        project_count = 0
    
    # Check ML models
    ml_status = 'loaded' if ml_service and ml_service.models_loaded else 'not_loaded'
    
    # Check dataset
    dataset_exists = os.path.exists(app.config['DATASET_PATH'])
    
    return jsonify({
        'status': 'healthy' if db_status == 'connected' else 'degraded',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'services': {
            'database': {
                'status': db_status,
                'project_count': project_count
            },
            'ml_models': {
                'status': ml_status,
                'service_available': ml_service is not None
            },
            'dataset': {
                'exists': dataset_exists,
                'path': app.config['DATASET_PATH']
            }
        },
        'api_info': {
            'total_endpoints': len([rule.rule for rule in app.url_map.iter_rules() if rule.rule.startswith('/api/')]),
            'cors_enabled': True,
            'debug_mode': app.config['DEBUG']
        }
    })

# List all endpoints
@app.route('/api/endpoints', methods=['GET'])
def list_endpoints():
    """List all available API endpoints"""
    endpoints = []
    for rule in app.url_map.iter_rules():
        if rule.rule.startswith('/api/'):
            endpoints.append({
                'endpoint': rule.rule,
                'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                'resource': rule.endpoint
            })
    
    return jsonify({
        'success': True,
        'total_endpoints': len(endpoints),
        'endpoints': sorted(endpoints, key=lambda x: x['endpoint']),
        'categories': {
            'predictions': len([e for e in endpoints if '/predictions/' in e['endpoint']]),
            'projects': len([e for e in endpoints if '/projects/' in e['endpoint']]),
            'analytics': len([e for e in endpoints if '/analytics/' in e['endpoint']]),
            'chatbot': len([e for e in endpoints if '/chatbot' in e['endpoint']]),
            'scheduler': len([e for e in endpoints if '/scheduler/' in e['endpoint']]),
            'geospatial': len([e for e in endpoints if '/geospatial/' in e['endpoint']])
        }
    })

# Legacy endpoints for backward compatibility
@app.route('/api/projects/stats/summary', methods=['GET'])
def legacy_project_stats():
    """Legacy endpoint for project statistics"""
    from api.projects import ProjectStatsResource
    resource = ProjectStatsResource()
    return resource.get()

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Not found',
        'message': 'The requested resource was not found',
        'available_endpoints': '/api/endpoints'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An internal server error occurred'
    }), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 'Bad request',
        'message': 'Invalid request data or format'
    }), 400

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Method not allowed',
        'message': 'HTTP method not allowed for this endpoint'
    }), 405

# Application initialization function
def initialize_app():
    """Create database tables and initialize services"""
    try:
        # Create all tables
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
            
            # Load ML models if dataset exists
            if ml_service and os.path.exists(app.config['DATASET_PATH']):
                try:
                    success = ml_service.train_models(app.config['DATASET_PATH'], save_models=True)
                    if success:
                        logger.info("ML models trained and loaded successfully")
                    else:
                        logger.warning("ML models training failed")
                except Exception as e:
                    logger.error(f"Error training ML models: {str(e)}")
            
            # Initialize regional data if not exists
            try:
                if RegionalData.query.count() == 0:
                    # Create some sample regional data
                    sample_regions = [
                        RegionalData(
                            region_id='WR',
                            region_name='Western Region',
                            economic_index=1.2,
                            environmental_risk=0.6,
                            infrastructure_quality=0.8,
                            regulatory_efficiency=0.7,
                            labor_availability=0.9
                        ),
                        RegionalData(
                            region_id='NR',
                            region_name='Northern Region',
                            economic_index=1.1,
                            environmental_risk=0.5,
                            infrastructure_quality=0.9,
                            regulatory_efficiency=0.8,
                            labor_availability=0.8
                        )
                    ]
                    
                    for region in sample_regions:
                        db.session.add(region)
                    
                    db.session.commit()
                    logger.info("Sample regional data initialized")
                    
            except Exception as e:
                logger.error(f"Error initializing regional data: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}")

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs(app.config['MODEL_DIR'], exist_ok=True)
    
    # Initialize the application
    initialize_app()
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting PowerGrid ML Backend on port {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    )