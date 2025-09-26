"""
API endpoints for project CRUD operations
"""

from flask import request, jsonify
from flask_restful import Resource
from datetime import datetime
import logging
from models.project_model import Project
from models.regional_data import RegionalData
from services.prediction_service import PredictionService

logger = logging.getLogger(__name__)

class ProjectResource(Resource):
    """
    Resource for handling individual project operations
    """
    
    def __init__(self):
        self.prediction_service = PredictionService()
    
    def get(self, project_id=None):
        """
        Get project details by ID or list all projects
        """
        try:
            from app import db
            
            if project_id:
                # Get specific project
                project = Project.query.filter_by(project_id=project_id).first()
                if not project:
                    return {
                        'success': False,
                        'message': f'Project {project_id} not found'
                    }, 404
                
                project_data = project.to_dict()
                
                # Include predictions if available
                predictions = project.get_predictions()
                if predictions:
                    project_data['predictions'] = predictions
                
                return {
                    'success': True,
                    'data': project_data
                }, 200
            
            else:
                # Get all projects with pagination
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 50, type=int)
                status_filter = request.args.get('status')
                risk_filter = request.args.get('risk')
                project_type = request.args.get('project_type')
                
                # Build query
                query = Project.query
                
                if status_filter:
                    query = query.filter(Project.status == status_filter)
                
                if risk_filter:
                    query = query.filter(Project.risk == risk_filter)
                
                if project_type:
                    query = query.filter(Project.project_type == project_type)
                
                # Get paginated results
                projects = query.paginate(
                    page=page,
                    per_page=per_page,
                    error_out=False
                )
                
                projects_data = []
                for project in projects.items:
                    project_dict = project.to_dict()
                    # Add summary predictions
                    predictions = project.get_predictions()
                    if predictions:
                        project_dict['risk_score'] = predictions.get('risk_score', 0)
                        project_dict['confidence_score'] = predictions.get('confidence_score', 0)
                    
                    projects_data.append(project_dict)
                
                return {
                    'success': True,
                    'data': {
                        'projects': projects_data,
                        'pagination': {
                            'page': page,
                            'per_page': per_page,
                            'total_pages': projects.pages,
                            'total_items': projects.total,
                            'has_next': projects.has_next,
                            'has_prev': projects.has_prev
                        }
                    }
                }, 200
                
        except Exception as e:
            logger.error(f"Error getting project data: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500
    
    def post(self):
        """
        Create a new project
        
        Expected JSON format:
        {
            "name": "New Substation Project",
            "project_type": "substation",
            "location": "Maharashtra/Mumbai",
            "base_estimated_cost": 1500.0,
            "planned_timeline_months": 18,
            "terrain_type": "urban",
            "labour_wage_rate": 450.0,
            ...other fields
        }
        """
        try:
            if not request.json:
                return {
                    'success': False,
                    'message': 'No JSON data provided'
                }, 400
            
            data = request.json
            
            # Validate required fields
            required_fields = ['name', 'project_type', 'location', 'base_estimated_cost']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return {
                    'success': False,
                    'message': f'Missing required fields: {", ".join(missing_fields)}'
                }, 400
            
            from app import db
            
            # Create new project
            project = Project()
            
            # Set basic fields
            project.name = data['name']
            project.project_type = data['project_type']
            project.location = data['location']
            project.base_estimated_cost = data['base_estimated_cost']
            
            # Set optional fields with defaults
            project.planned_timeline_months = data.get('planned_timeline_months', 12)
            project.terrain_type = data.get('terrain_type', 'rural')
            project.labour_wage_rate = data.get('labour_wage_rate', 400.0)
            project.steel_price_index = data.get('steel_price_index', 100.0)
            project.cement_price_index = data.get('cement_price_index', 100.0)
            project.vendor_reliability_score = data.get('vendor_reliability_score', 0.7)
            project.material_availability_index = data.get('material_availability_index', 0.8)
            project.skilled_manpower_availability = data.get('skilled_manpower_availability', 70)
            project.regulatory_delay_estimate = data.get('regulatory_delay_estimate', 1.0)
            project.historical_delay_pattern = data.get('historical_delay_pattern', 'low')
            project.annual_rainfall = data.get('annual_rainfall', 100.0)
            project.demand_supply_pressure = data.get('demand_supply_pressure', 'medium')
            
            # Set status and timestamps
            project.status = 'Planning'
            project.created_at = datetime.utcnow()
            project.updated_at = datetime.utcnow()
            
            # Generate project ID
            import uuid
            project.project_id = f"PG{str(uuid.uuid4())[:8].upper()}"
            
            # Save to database
            db.session.add(project)
            db.session.commit()
            
            # Run initial prediction if enough data is provided
            try:
                predictions = self.prediction_service.predict_project_outcomes(data)
                project.set_predictions(predictions)
                project.last_prediction_date = datetime.utcnow()
                db.session.commit()
                
                logger.info(f"Initial predictions generated for project {project.project_id}")
                
            except Exception as pred_e:
                logger.warning(f"Could not generate initial predictions for project {project.project_id}: {str(pred_e)}")
            
            project_dict = project.to_dict()
            predictions = project.get_predictions()
            if predictions:
                project_dict['predictions'] = predictions
            
            return {
                'success': True,
                'data': project_dict,
                'message': f'Project {project.project_id} created successfully'
            }, 201
            
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500
    
    def put(self, project_id):
        """
        Update an existing project
        """
        try:
            if not request.json:
                return {
                    'success': False,
                    'message': 'No JSON data provided'
                }, 400
            
            from app import db
            
            project = Project.query.filter_by(project_id=project_id).first()
            if not project:
                return {
                    'success': False,
                    'message': f'Project {project_id} not found'
                }, 404
            
            data = request.json
            
            # Update fields that are provided
            updatable_fields = [
                'name', 'project_type', 'location', 'base_estimated_cost',
                'planned_timeline_months', 'terrain_type', 'labour_wage_rate',
                'steel_price_index', 'cement_price_index', 'vendor_reliability_score',
                'material_availability_index', 'skilled_manpower_availability',
                'regulatory_delay_estimate', 'historical_delay_pattern',
                'annual_rainfall', 'demand_supply_pressure', 'status'
            ]
            
            updated_fields = []
            for field in updatable_fields:
                if field in data:
                    setattr(project, field, data[field])
                    updated_fields.append(field)
            
            if updated_fields:
                project.updated_at = datetime.utcnow()
                db.session.commit()
                
                # Regenerate predictions if significant fields were updated
                prediction_fields = [
                    'base_estimated_cost', 'planned_timeline_months', 'terrain_type',
                    'labour_wage_rate', 'vendor_reliability_score', 'material_availability_index'
                ]
                
                if any(field in updated_fields for field in prediction_fields):
                    try:
                        predictions = self.prediction_service.predict_project_outcomes(project.to_ml_features())
                        project.set_predictions(predictions)
                        project.last_prediction_date = datetime.utcnow()
                        db.session.commit()
                        
                        logger.info(f"Predictions updated for project {project_id}")
                        
                    except Exception as pred_e:
                        logger.warning(f"Could not update predictions for project {project_id}: {str(pred_e)}")
                
                project_dict = project.to_dict()
                predictions = project.get_predictions()
                if predictions:
                    project_dict['predictions'] = predictions
                
                return {
                    'success': True,
                    'data': project_dict,
                    'message': f'Project {project_id} updated successfully',
                    'updated_fields': updated_fields
                }, 200
            
            else:
                return {
                    'success': True,
                    'message': 'No fields to update',
                    'data': project.to_dict()
                }, 200
                
        except Exception as e:
            logger.error(f"Error updating project: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500
    
    def delete(self, project_id):
        """
        Delete a project
        """
        try:
            from app import db
            
            project = Project.query.filter_by(project_id=project_id).first()
            if not project:
                return {
                    'success': False,
                    'message': f'Project {project_id} not found'
                }, 404
            
            # Store project info before deletion
            project_name = project.name
            
            # Delete project
            db.session.delete(project)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Project {project_id} ({project_name}) deleted successfully'
            }, 200
            
        except Exception as e:
            logger.error(f"Error deleting project: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500


class ProjectStatsResource(Resource):
    """
    Resource for getting project statistics and summaries
    """
    
    def get(self):
        """
        Get project statistics and summaries
        """
        try:
            from app import db
            from sqlalchemy import func
            
            # Basic counts
            total_projects = Project.query.count()
            
            # Status distribution
            status_stats = db.session.query(
                Project.status,
                func.count(Project.id).label('count')
            ).group_by(Project.status).all()
            
            # Risk distribution
            risk_stats = db.session.query(
                Project.risk,
                func.count(Project.id).label('count')
            ).group_by(Project.risk).all()
            
            # Project type distribution
            type_stats = db.session.query(
                Project.project_type,
                func.count(Project.id).label('count')
            ).group_by(Project.project_type).all()
            
            # Cost statistics
            cost_stats = db.session.query(
                func.avg(Project.base_estimated_cost).label('avg_cost'),
                func.min(Project.base_estimated_cost).label('min_cost'),
                func.max(Project.base_estimated_cost).label('max_cost'),
                func.sum(Project.base_estimated_cost).label('total_cost')
            ).first()
            
            # Timeline statistics
            timeline_stats = db.session.query(
                func.avg(Project.planned_timeline_months).label('avg_timeline'),
                func.min(Project.planned_timeline_months).label('min_timeline'),
                func.max(Project.planned_timeline_months).label('max_timeline')
            ).first()
            
            # Get recent projects
            recent_projects = Project.query.order_by(
                Project.created_at.desc()
            ).limit(10).all()
            
            return {
                'success': True,
                'data': {
                    'summary': {
                        'total_projects': total_projects,
                        'status_distribution': {item.status: item.count for item in status_stats},
                        'risk_distribution': {item.risk or 'Unknown': item.count for item in risk_stats},
                        'type_distribution': {item.project_type: item.count for item in type_stats}
                    },
                    'cost_statistics': {
                        'average_cost': round(cost_stats.avg_cost or 0, 2),
                        'minimum_cost': cost_stats.min_cost or 0,
                        'maximum_cost': cost_stats.max_cost or 0,
                        'total_portfolio_value': round(cost_stats.total_cost or 0, 2)
                    },
                    'timeline_statistics': {
                        'average_timeline_months': round(timeline_stats.avg_timeline or 0, 1),
                        'minimum_timeline_months': timeline_stats.min_timeline or 0,
                        'maximum_timeline_months': timeline_stats.max_timeline or 0
                    },
                    'recent_projects': [{
                        'project_id': p.project_id,
                        'name': p.name,
                        'project_type': p.project_type,
                        'status': p.status,
                        'risk': p.risk,
                        'created_at': p.created_at.isoformat() if p.created_at else None
                    } for p in recent_projects]
                }
            }, 200
            
        except Exception as e:
            logger.error(f"Error getting project statistics: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500


class ProjectSearchResource(Resource):
    """
    Resource for searching projects
    """
    
    def post(self):
        """
        Search projects based on various criteria
        
        Expected JSON format:
        {
            "query": "substation",
            "filters": {
                "project_type": "substation",
                "status": "active",
                "risk": "high",
                "location": "Maharashtra",
                "cost_range": {"min": 1000, "max": 5000}
            },
            "sort_by": "created_at",
            "sort_order": "desc",
            "page": 1,
            "per_page": 20
        }
        """
        try:
            from app import db
            from sqlalchemy import or_, and_
            
            data = request.json or {}
            
            query = data.get('query', '')
            filters = data.get('filters', {})
            sort_by = data.get('sort_by', 'created_at')
            sort_order = data.get('sort_order', 'desc')
            page = data.get('page', 1)
            per_page = data.get('per_page', 20)
            
            # Start building query
            search_query = Project.query
            
            # Text search in name, project_id, and location
            if query:
                search_query = search_query.filter(
                    or_(
                        Project.name.contains(query),
                        Project.project_id.contains(query),
                        Project.location.contains(query)
                    )
                )
            
            # Apply filters
            if 'project_type' in filters:
                search_query = search_query.filter(Project.project_type == filters['project_type'])
            
            if 'status' in filters:
                search_query = search_query.filter(Project.status == filters['status'])
            
            if 'risk' in filters:
                search_query = search_query.filter(Project.risk == filters['risk'])
            
            if 'location' in filters:
                search_query = search_query.filter(Project.location.contains(filters['location']))
            
            if 'cost_range' in filters:
                cost_range = filters['cost_range']
                if 'min' in cost_range:
                    search_query = search_query.filter(Project.base_estimated_cost >= cost_range['min'])
                if 'max' in cost_range:
                    search_query = search_query.filter(Project.base_estimated_cost <= cost_range['max'])
            
            # Apply sorting
            if hasattr(Project, sort_by):
                sort_column = getattr(Project, sort_by)
                if sort_order.lower() == 'desc':
                    search_query = search_query.order_by(sort_column.desc())
                else:
                    search_query = search_query.order_by(sort_column.asc())
            
            # Get paginated results
            results = search_query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            projects_data = []
            for project in results.items:
                project_dict = project.to_dict()
                predictions = project.get_predictions()
                if predictions:
                    project_dict['risk_score'] = predictions.get('risk_score', 0)
                    project_dict['confidence_score'] = predictions.get('confidence_score', 0)
                
                projects_data.append(project_dict)
            
            return {
                'success': True,
                'data': {
                    'projects': projects_data,
                    'search_info': {
                        'query': query,
                        'filters': filters,
                        'sort_by': sort_by,
                        'sort_order': sort_order
                    },
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total_pages': results.pages,
                        'total_items': results.total,
                        'has_next': results.has_next,
                        'has_prev': results.has_prev
                    }
                }
            }, 200
            
        except Exception as e:
            logger.error(f"Error searching projects: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500