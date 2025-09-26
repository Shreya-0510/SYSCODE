"""
API endpoints for analytics and dashboard data
"""

from flask import request, jsonify
from flask_restful import Resource
from datetime import datetime, timedelta
import logging
from models.analytics import Analytics
from models.project_model import Project

logger = logging.getLogger(__name__)

class AnalyticsResource(Resource):
    """
    Resource for getting analytics data for dashboards
    """
    
    def get(self, analytics_type=None):
        """
        Get analytics data
        
        Types: overview, trends, performance, risk_analysis, regional_analysis
        """
        try:
            from app import db
            from sqlalchemy import func, extract
            
            if analytics_type == 'overview':
                return self._get_overview_analytics()
            elif analytics_type == 'trends':
                return self._get_trend_analytics()
            elif analytics_type == 'performance':
                return self._get_performance_analytics()
            elif analytics_type == 'risk_analysis':
                return self._get_risk_analytics()
            elif analytics_type == 'regional_analysis':
                return self._get_regional_analytics()
            else:
                # Return comprehensive analytics
                return self._get_comprehensive_analytics()
                
        except Exception as e:
            logger.error(f"Error getting analytics data: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500
    
    def _get_overview_analytics(self):
        """Get high-level overview analytics"""
        from app import db
        from sqlalchemy import func
        
        # Key metrics
        total_projects = Project.query.count()
        active_projects = Project.query.filter(Project.status.in_(['Planning', 'In Progress'])).count()
        completed_projects = Project.query.filter(Project.status == 'Completed').count()
        
        # Cost metrics
        total_portfolio_value = db.session.query(
            func.sum(Project.base_estimated_cost)
        ).scalar() or 0
        
        avg_project_cost = db.session.query(
            func.avg(Project.base_estimated_cost)
        ).scalar() or 0
        
        # Risk distribution
        risk_distribution = db.session.query(
            Project.risk,
            func.count(Project.id).label('count')
        ).group_by(Project.risk).all()
        
        # Timeline metrics
        avg_timeline = db.session.query(
            func.avg(Project.planned_timeline_months)
        ).scalar() or 0
        
        # Predictions summary (if available)
        projects_with_predictions = Project.query.filter(
            Project.last_prediction_date.isnot(None)
        ).count()
        
        return {
            'success': True,
            'data': {
                'key_metrics': {
                    'total_projects': total_projects,
                    'active_projects': active_projects,
                    'completed_projects': completed_projects,
                    'completion_rate': round(completed_projects / total_projects * 100, 1) if total_projects > 0 else 0
                },
                'financial_metrics': {
                    'total_portfolio_value': round(total_portfolio_value, 2),
                    'average_project_cost': round(avg_project_cost, 2),
                    'active_portfolio_value': self._get_active_portfolio_value()
                },
                'risk_distribution': {
                    item.risk or 'Unknown': item.count for item in risk_distribution
                },
                'performance_metrics': {
                    'average_timeline_months': round(avg_timeline, 1),
                    'projects_with_predictions': projects_with_predictions,
                    'prediction_coverage': round(projects_with_predictions / total_projects * 100, 1) if total_projects > 0 else 0
                }
            }
        }, 200
    
    def _get_trend_analytics(self):
        """Get trend analytics over time"""
        from app import db
        from sqlalchemy import func, extract
        
        # Project creation trends (last 12 months)
        twelve_months_ago = datetime.utcnow() - timedelta(days=365)
        
        monthly_projects = db.session.query(
            extract('year', Project.created_at).label('year'),
            extract('month', Project.created_at).label('month'),
            func.count(Project.id).label('count')
        ).filter(
            Project.created_at >= twelve_months_ago
        ).group_by(
            extract('year', Project.created_at),
            extract('month', Project.created_at)
        ).order_by('year', 'month').all()
        
        # Cost trends
        monthly_costs = db.session.query(
            extract('year', Project.created_at).label('year'),
            extract('month', Project.created_at).label('month'),
            func.sum(Project.base_estimated_cost).label('total_cost'),
            func.avg(Project.base_estimated_cost).label('avg_cost')
        ).filter(
            Project.created_at >= twelve_months_ago
        ).group_by(
            extract('year', Project.created_at),
            extract('month', Project.created_at)
        ).order_by('year', 'month').all()
        
        # Status progression over time
        status_trends = []
        for i in range(6):  # Last 6 months
            month_start = datetime.utcnow() - timedelta(days=30 * (i + 1))
            month_end = datetime.utcnow() - timedelta(days=30 * i)
            
            monthly_status = db.session.query(
                Project.status,
                func.count(Project.id).label('count')
            ).filter(
                Project.created_at >= month_start,
                Project.created_at < month_end
            ).group_by(Project.status).all()
            
            status_trends.append({
                'month': month_start.strftime('%Y-%m'),
                'status_distribution': {item.status: item.count for item in monthly_status}
            })
        
        return {
            'success': True,
            'data': {
                'project_creation_trends': [
                    {
                        'period': f"{int(item.year)}-{int(item.month):02d}",
                        'project_count': item.count
                    } for item in monthly_projects
                ],
                'cost_trends': [
                    {
                        'period': f"{int(item.year)}-{int(item.month):02d}",
                        'total_cost': round(item.total_cost or 0, 2),
                        'average_cost': round(item.avg_cost or 0, 2)
                    } for item in monthly_costs
                ],
                'status_trends': status_trends
            }
        }, 200
    
    def _get_performance_analytics(self):
        """Get performance analytics"""
        from app import db
        from sqlalchemy import func
        
        # Performance by project type
        type_performance = db.session.query(
            Project.project_type,
            func.count(Project.id).label('total_projects'),
            func.avg(Project.base_estimated_cost).label('avg_cost'),
            func.avg(Project.planned_timeline_months).label('avg_timeline')
        ).group_by(Project.project_type).all()
        
        # Performance by risk level
        risk_performance = db.session.query(
            Project.risk,
            func.count(Project.id).label('total_projects'),
            func.avg(Project.base_estimated_cost).label('avg_cost'),
            func.avg(Project.planned_timeline_months).label('avg_timeline')
        ).group_by(Project.risk).all()
        
        # Performance by terrain type
        terrain_performance = db.session.query(
            Project.terrain_type,
            func.count(Project.id).label('total_projects'),
            func.avg(Project.base_estimated_cost).label('avg_cost'),
            func.avg(Project.planned_timeline_months).label('avg_timeline')
        ).group_by(Project.terrain_type).all()
        
        # Cost vs Timeline correlation
        cost_timeline_data = db.session.query(
            Project.base_estimated_cost,
            Project.planned_timeline_months,
            Project.project_type,
            Project.risk
        ).filter(
            Project.base_estimated_cost.isnot(None),
            Project.planned_timeline_months.isnot(None)
        ).all()
        
        return {
            'success': True,
            'data': {
                'project_type_performance': [
                    {
                        'project_type': item.project_type,
                        'total_projects': item.total_projects,
                        'average_cost': round(item.avg_cost or 0, 2),
                        'average_timeline_months': round(item.avg_timeline or 0, 1)
                    } for item in type_performance
                ],
                'risk_level_performance': [
                    {
                        'risk_level': item.risk or 'Unknown',
                        'total_projects': item.total_projects,
                        'average_cost': round(item.avg_cost or 0, 2),
                        'average_timeline_months': round(item.avg_timeline or 0, 1)
                    } for item in risk_performance
                ],
                'terrain_performance': [
                    {
                        'terrain_type': item.terrain_type,
                        'total_projects': item.total_projects,
                        'average_cost': round(item.avg_cost or 0, 2),
                        'average_timeline_months': round(item.avg_timeline or 0, 1)
                    } for item in terrain_performance
                ],
                'cost_timeline_correlation': [
                    {
                        'cost': item.base_estimated_cost,
                        'timeline': item.planned_timeline_months,
                        'project_type': item.project_type,
                        'risk': item.risk
                    } for item in cost_timeline_data[:100]  # Limit for performance
                ]
            }
        }, 200
    
    def _get_risk_analytics(self):
        """Get risk analytics"""
        from app import db
        from sqlalchemy import func
        
        # Risk distribution by project type
        risk_by_type = db.session.query(
            Project.project_type,
            Project.risk,
            func.count(Project.id).label('count')
        ).group_by(Project.project_type, Project.risk).all()
        
        # Risk factors analysis
        risk_factors = {
            'high_risk_projects': Project.query.filter(Project.risk == 'High').count(),
            'medium_risk_projects': Project.query.filter(Project.risk == 'Medium').count(),
            'low_risk_projects': Project.query.filter(Project.risk == 'Low').count()
        }
        
        # High-risk projects details
        high_risk_projects = Project.query.filter(Project.risk == 'High').all()
        
        # Vendor reliability impact
        vendor_risk_analysis = db.session.query(
            func.case(
                [(Project.vendor_reliability_score < 0.5, 'Low Reliability'),
                 (Project.vendor_reliability_score < 0.7, 'Medium Reliability')],
                else_='High Reliability'
            ).label('reliability_category'),
            Project.risk,
            func.count(Project.id).label('count')
        ).group_by('reliability_category', Project.risk).all()
        
        return {
            'success': True,
            'data': {
                'risk_distribution': risk_factors,
                'risk_by_project_type': [
                    {
                        'project_type': item.project_type,
                        'risk_level': item.risk or 'Unknown',
                        'count': item.count
                    } for item in risk_by_type
                ],
                'high_risk_projects': [
                    {
                        'project_id': p.project_id,
                        'name': p.name,
                        'project_type': p.project_type,
                        'cost': p.base_estimated_cost,
                        'timeline': p.planned_timeline_months,
                        'predictions': p.get_predictions()
                    } for p in high_risk_projects[:20]  # Top 20
                ],
                'vendor_reliability_impact': [
                    {
                        'reliability_category': item.reliability_category,
                        'risk_level': item.risk or 'Unknown',
                        'count': item.count
                    } for item in vendor_risk_analysis
                ]
            }
        }, 200
    
    def _get_regional_analytics(self):
        """Get regional analytics"""
        from app import db
        from sqlalchemy import func
        
        # Projects by location/state
        location_stats = db.session.query(
            Project.location,
            func.count(Project.id).label('project_count'),
            func.avg(Project.base_estimated_cost).label('avg_cost'),
            func.sum(Project.base_estimated_cost).label('total_cost')
        ).group_by(Project.location).all()
        
        # Extract state-level data
        state_stats = {}
        for item in location_stats:
            if '/' in item.location:
                state = item.location.split('/')[0]
                if state not in state_stats:
                    state_stats[state] = {
                        'project_count': 0,
                        'total_cost': 0,
                        'locations': []
                    }
                state_stats[state]['project_count'] += item.project_count
                state_stats[state]['total_cost'] += item.total_cost or 0
                state_stats[state]['locations'].append({
                    'location': item.location,
                    'project_count': item.project_count,
                    'avg_cost': round(item.avg_cost or 0, 2)
                })
        
        # Regional performance metrics
        regional_performance = []
        for state, data in state_stats.items():
            avg_cost_per_project = data['total_cost'] / data['project_count'] if data['project_count'] > 0 else 0
            regional_performance.append({
                'state': state,
                'total_projects': data['project_count'],
                'total_investment': round(data['total_cost'], 2),
                'average_cost_per_project': round(avg_cost_per_project, 2),
                'locations': data['locations']
            })
        
        # Sort by total investment
        regional_performance.sort(key=lambda x: x['total_investment'], reverse=True)
        
        return {
            'success': True,
            'data': {
                'location_distribution': [
                    {
                        'location': item.location,
                        'project_count': item.project_count,
                        'average_cost': round(item.avg_cost or 0, 2),
                        'total_cost': round(item.total_cost or 0, 2)
                    } for item in location_stats
                ],
                'state_wise_analysis': regional_performance,
                'regional_summary': {
                    'total_states_covered': len(state_stats),
                    'total_locations': len(location_stats),
                    'highest_investment_state': regional_performance[0]['state'] if regional_performance else None,
                    'most_projects_state': max(state_stats.items(), key=lambda x: x[1]['project_count'])[0] if state_stats else None
                }
            }
        }, 200
    
    def _get_comprehensive_analytics(self):
        """Get comprehensive analytics combining all types"""
        overview = self._get_overview_analytics()[0]['data']
        trends = self._get_trend_analytics()[0]['data']
        performance = self._get_performance_analytics()[0]['data']
        risk = self._get_risk_analytics()[0]['data']
        regional = self._get_regional_analytics()[0]['data']
        
        return {
            'success': True,
            'data': {
                'overview': overview,
                'trends': trends,
                'performance': performance,
                'risk_analysis': risk,
                'regional_analysis': regional,
                'generated_at': datetime.utcnow().isoformat()
            }
        }, 200
    
    def _get_active_portfolio_value(self):
        """Calculate total value of active projects"""
        from app import db
        from sqlalchemy import func
        
        active_value = db.session.query(
            func.sum(Project.base_estimated_cost)
        ).filter(
            Project.status.in_(['Planning', 'In Progress'])
        ).scalar() or 0
        
        return round(active_value, 2)


class AnalyticsExportResource(Resource):
    """
    Resource for exporting analytics data
    """
    
    def post(self):
        """
        Export analytics data in specified format
        
        Expected JSON format:
        {
            "export_type": "overview|trends|performance|risk|regional|comprehensive",
            "format": "json|csv",
            "date_range": {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            }
        }
        """
        try:
            data = request.json or {}
            export_type = data.get('export_type', 'comprehensive')
            format_type = data.get('format', 'json')
            date_range = data.get('date_range')
            
            # Get analytics data
            analytics_resource = AnalyticsResource()
            
            if export_type == 'comprehensive':
                result = analytics_resource._get_comprehensive_analytics()
            elif export_type == 'overview':
                result = analytics_resource._get_overview_analytics()
            elif export_type == 'trends':
                result = analytics_resource._get_trend_analytics()
            elif export_type == 'performance':
                result = analytics_resource._get_performance_analytics()
            elif export_type == 'risk':
                result = analytics_resource._get_risk_analytics()
            elif export_type == 'regional':
                result = analytics_resource._get_regional_analytics()
            else:
                return {
                    'success': False,
                    'message': f'Unknown export type: {export_type}'
                }, 400
            
            if format_type == 'json':
                # Return JSON data with export metadata
                export_data = result[0]['data']
                export_data['export_metadata'] = {
                    'export_type': export_type,
                    'format': format_type,
                    'generated_at': datetime.utcnow().isoformat(),
                    'date_range': date_range
                }
                
                return {
                    'success': True,
                    'data': export_data
                }, 200
            
            elif format_type == 'csv':
                # Convert to CSV format (simplified version)
                import io
                import csv
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write CSV based on export type
                if export_type == 'overview':
                    writer.writerow(['Metric', 'Value'])
                    data = result[0]['data']
                    for section, metrics in data.items():
                        if isinstance(metrics, dict):
                            for key, value in metrics.items():
                                writer.writerow([f"{section}_{key}", value])
                        else:
                            writer.writerow([section, metrics])
                
                csv_data = output.getvalue()
                output.close()
                
                return {
                    'success': True,
                    'data': {
                        'csv_data': csv_data,
                        'export_metadata': {
                            'export_type': export_type,
                            'format': format_type,
                            'generated_at': datetime.utcnow().isoformat(),
                            'rows': len(csv_data.split('\n')) - 1
                        }
                    }
                }, 200
            
            else:
                return {
                    'success': False,
                    'message': f'Unsupported format: {format_type}'
                }, 400
                
        except Exception as e:
            logger.error(f"Error exporting analytics data: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error during export'
            }, 500