"""
API endpoints for scheduler and task management
"""

from flask import request, jsonify
from flask_restful import Resource
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SchedulerResource(Resource):
    """
    Resource for managing scheduled tasks and project timelines
    """
    
    def get(self, schedule_type=None):
        """
        Get scheduled tasks and project timelines
        
        Types: upcoming, overdue, milestones, maintenance
        """
        try:
            if schedule_type == 'upcoming':
                return self._get_upcoming_tasks()
            elif schedule_type == 'overdue':
                return self._get_overdue_tasks()
            elif schedule_type == 'milestones':
                return self._get_project_milestones()
            elif schedule_type == 'maintenance':
                return self._get_maintenance_schedule()
            else:
                return self._get_comprehensive_schedule()
                
        except Exception as e:
            logger.error(f"Error getting schedule data: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500
    
    def post(self):
        """
        Create new scheduled task
        
        Expected JSON format:
        {
            "title": "Site Inspection",
            "description": "Monthly site inspection for safety compliance",
            "project_id": "PG4001",
            "task_type": "inspection",
            "priority": "high",
            "scheduled_date": "2024-01-15T10:00:00",
            "duration_hours": 4,
            "assigned_to": "inspector@powergrid.com",
            "recurring": {
                "enabled": true,
                "frequency": "monthly",
                "end_date": "2024-12-31"
            }
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
            required_fields = ['title', 'scheduled_date', 'task_type']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return {
                    'success': False,
                    'message': f'Missing required fields: {", ".join(missing_fields)}'
                }, 400
            
            # Create scheduled task
            task = self._create_scheduled_task(data)
            
            return {
                'success': True,
                'data': task,
                'message': 'Scheduled task created successfully'
            }, 201
            
        except Exception as e:
            logger.error(f"Error creating scheduled task: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500
    
    def _get_upcoming_tasks(self):
        """Get tasks scheduled for the next 30 days"""
        from models.project_model import Project
        
        # Mock upcoming tasks - in production this would query a tasks table
        upcoming_tasks = [
            {
                'task_id': 'T001',
                'title': 'Substation Site Survey',
                'project_id': 'PG4001',
                'project_name': 'Mumbai North Substation',
                'task_type': 'survey',
                'priority': 'high',
                'scheduled_date': (datetime.utcnow() + timedelta(days=2)).isoformat(),
                'duration_hours': 8,
                'assigned_to': 'survey.team@powergrid.com',
                'status': 'scheduled',
                'location': 'Maharashtra/Mumbai'
            },
            {
                'task_id': 'T002',
                'title': 'Environmental Clearance Review',
                'project_id': 'PG4002',
                'project_name': 'Delhi East Transmission Line',
                'task_type': 'regulatory',
                'priority': 'medium',
                'scheduled_date': (datetime.utcnow() + timedelta(days=5)).isoformat(),
                'duration_hours': 4,
                'assigned_to': 'env.team@powergrid.com',
                'status': 'scheduled',
                'location': 'Delhi/East Delhi'
            },
            {
                'task_id': 'T003',
                'title': 'Material Procurement Review',
                'project_id': 'PG4003',
                'project_name': 'Karnataka Grid Expansion',
                'task_type': 'procurement',
                'priority': 'high',
                'scheduled_date': (datetime.utcnow() + timedelta(days=7)).isoformat(),
                'duration_hours': 6,
                'assigned_to': 'procurement@powergrid.com',
                'status': 'scheduled',
                'location': 'Karnataka/Bangalore'
            },
            {
                'task_id': 'T004',
                'title': 'Safety Compliance Audit',
                'project_id': 'PG4001',
                'project_name': 'Mumbai North Substation',
                'task_type': 'audit',
                'priority': 'critical',
                'scheduled_date': (datetime.utcnow() + timedelta(days=10)).isoformat(),
                'duration_hours': 12,
                'assigned_to': 'safety@powergrid.com',
                'status': 'scheduled',
                'location': 'Maharashtra/Mumbai'
            },
            {
                'task_id': 'T005',
                'title': 'Progress Review Meeting',
                'project_id': 'PG4004',
                'project_name': 'Tamil Nadu Coastal Project',
                'task_type': 'review',
                'priority': 'medium',
                'scheduled_date': (datetime.utcnow() + timedelta(days=14)).isoformat(),
                'duration_hours': 3,
                'assigned_to': 'project.manager@powergrid.com',
                'status': 'scheduled',
                'location': 'Tamil Nadu/Chennai'
            }
        ]
        
        return {
            'success': True,
            'data': {
                'upcoming_tasks': upcoming_tasks,
                'total_count': len(upcoming_tasks),
                'next_7_days': len([t for t in upcoming_tasks if 
                                  datetime.fromisoformat(t['scheduled_date'].replace('Z', '')) <= 
                                  datetime.utcnow() + timedelta(days=7)])
            }
        }, 200
    
    def _get_overdue_tasks(self):
        """Get overdue tasks that need immediate attention"""
        
        # Mock overdue tasks
        overdue_tasks = [
            {
                'task_id': 'T010',
                'title': 'Land Acquisition Approval',
                'project_id': 'PG4005',
                'project_name': 'Gujarat Wind Integration',
                'task_type': 'regulatory',
                'priority': 'critical',
                'scheduled_date': (datetime.utcnow() - timedelta(days=5)).isoformat(),
                'overdue_days': 5,
                'assigned_to': 'legal@powergrid.com',
                'status': 'overdue',
                'impact': 'Project timeline at risk'
            },
            {
                'task_id': 'T011',
                'title': 'Equipment Testing',
                'project_id': 'PG4006',
                'project_name': 'Rajasthan Solar Grid',
                'task_type': 'testing',
                'priority': 'high',
                'scheduled_date': (datetime.utcnow() - timedelta(days=2)).isoformat(),
                'overdue_days': 2,
                'assigned_to': 'testing@powergrid.com',
                'status': 'overdue',
                'impact': 'Commissioning delay possible'
            }
        ]
        
        return {
            'success': True,
            'data': {
                'overdue_tasks': overdue_tasks,
                'total_overdue': len(overdue_tasks),
                'critical_overdue': len([t for t in overdue_tasks if t['priority'] == 'critical']),
                'average_overdue_days': sum(t['overdue_days'] for t in overdue_tasks) / len(overdue_tasks) if overdue_tasks else 0
            }
        }, 200
    
    def _get_project_milestones(self):
        """Get project milestones and key dates"""
        
        # Mock project milestones
        milestones = [
            {
                'milestone_id': 'M001',
                'project_id': 'PG4001',
                'project_name': 'Mumbai North Substation',
                'milestone_type': 'construction_start',
                'title': 'Construction Phase Begins',
                'planned_date': (datetime.utcnow() + timedelta(days=30)).isoformat(),
                'status': 'on_track',
                'completion_percentage': 85,
                'dependencies': ['Land clearance', 'Material procurement']
            },
            {
                'milestone_id': 'M002',
                'project_id': 'PG4002',
                'project_name': 'Delhi East Transmission Line',
                'milestone_type': 'environmental_clearance',
                'title': 'Environmental Clearance Received',
                'planned_date': (datetime.utcnow() + timedelta(days=45)).isoformat(),
                'status': 'at_risk',
                'completion_percentage': 60,
                'dependencies': ['Impact assessment', 'Public consultation']
            },
            {
                'milestone_id': 'M003',
                'project_id': 'PG4003',
                'project_name': 'Karnataka Grid Expansion',
                'milestone_type': 'commissioning',
                'title': 'Phase 1 Commissioning',
                'planned_date': (datetime.utcnow() + timedelta(days=120)).isoformat(),
                'status': 'on_track',
                'completion_percentage': 25,
                'dependencies': ['Testing completion', 'Regulatory approval']
            }
        ]
        
        return {
            'success': True,
            'data': {
                'milestones': milestones,
                'total_milestones': len(milestones),
                'on_track': len([m for m in milestones if m['status'] == 'on_track']),
                'at_risk': len([m for m in milestones if m['status'] == 'at_risk']),
                'next_30_days': len([m for m in milestones if 
                                    datetime.fromisoformat(m['planned_date'].replace('Z', '')) <= 
                                    datetime.utcnow() + timedelta(days=30)])
            }
        }, 200
    
    def _get_maintenance_schedule(self):
        """Get maintenance and inspection schedule"""
        
        # Mock maintenance schedule
        maintenance_tasks = [
            {
                'maintenance_id': 'MNT001',
                'asset_id': 'SUB001',
                'asset_name': 'Mumbai North 400kV Substation',
                'maintenance_type': 'preventive',
                'task_title': 'Transformer Oil Analysis',
                'scheduled_date': (datetime.utcnow() + timedelta(days=15)).isoformat(),
                'frequency': 'quarterly',
                'priority': 'medium',
                'estimated_duration': 4,
                'assigned_team': 'Maintenance Team A',
                'status': 'scheduled'
            },
            {
                'maintenance_id': 'MNT002',
                'asset_id': 'LINE001',
                'asset_name': 'Delhi-Gurgaon 765kV Line',
                'maintenance_type': 'corrective',
                'task_title': 'Conductor Inspection',
                'scheduled_date': (datetime.utcnow() + timedelta(days=3)).isoformat(),
                'frequency': 'as_needed',
                'priority': 'high',
                'estimated_duration': 8,
                'assigned_team': 'Line Maintenance Team',
                'status': 'scheduled'
            },
            {
                'maintenance_id': 'MNT003',
                'asset_id': 'SUB002',
                'asset_name': 'Bangalore West Substation',
                'maintenance_type': 'preventive',
                'task_title': 'Circuit Breaker Testing',
                'scheduled_date': (datetime.utcnow() + timedelta(days=21)).isoformat(),
                'frequency': 'biannual',
                'priority': 'high',
                'estimated_duration': 6,
                'assigned_team': 'Testing Team B',
                'status': 'scheduled'
            }
        ]
        
        return {
            'success': True,
            'data': {
                'maintenance_tasks': maintenance_tasks,
                'total_tasks': len(maintenance_tasks),
                'preventive': len([t for t in maintenance_tasks if t['maintenance_type'] == 'preventive']),
                'corrective': len([t for t in maintenance_tasks if t['maintenance_type'] == 'corrective']),
                'next_week': len([t for t in maintenance_tasks if 
                                datetime.fromisoformat(t['scheduled_date'].replace('Z', '')) <= 
                                datetime.utcnow() + timedelta(days=7)])
            }
        }, 200
    
    def _get_comprehensive_schedule(self):
        """Get comprehensive schedule combining all types"""
        upcoming = self._get_upcoming_tasks()[0]['data']
        overdue = self._get_overdue_tasks()[0]['data']
        milestones = self._get_project_milestones()[0]['data']
        maintenance = self._get_maintenance_schedule()[0]['data']
        
        # Calendar view data for next 30 days
        calendar_events = []
        
        # Add upcoming tasks to calendar
        for task in upcoming['upcoming_tasks']:
            calendar_events.append({
                'date': task['scheduled_date'],
                'type': 'task',
                'title': task['title'],
                'project_id': task['project_id'],
                'priority': task['priority'],
                'duration': task['duration_hours']
            })
        
        # Add milestones to calendar
        for milestone in milestones['milestones']:
            if datetime.fromisoformat(milestone['planned_date'].replace('Z', '')) <= datetime.utcnow() + timedelta(days=30):
                calendar_events.append({
                    'date': milestone['planned_date'],
                    'type': 'milestone',
                    'title': milestone['title'],
                    'project_id': milestone['project_id'],
                    'priority': 'high' if milestone['status'] == 'at_risk' else 'medium',
                    'completion': milestone['completion_percentage']
                })
        
        # Add maintenance to calendar
        for mnt in maintenance['maintenance_tasks']:
            if datetime.fromisoformat(mnt['scheduled_date'].replace('Z', '')) <= datetime.utcnow() + timedelta(days=30):
                calendar_events.append({
                    'date': mnt['scheduled_date'],
                    'type': 'maintenance',
                    'title': mnt['task_title'],
                    'asset_id': mnt['asset_id'],
                    'priority': mnt['priority'],
                    'duration': mnt['estimated_duration']
                })
        
        # Sort events by date
        calendar_events.sort(key=lambda x: x['date'])
        
        return {
            'success': True,
            'data': {
                'upcoming_tasks': upcoming,
                'overdue_tasks': overdue,
                'project_milestones': milestones,
                'maintenance_schedule': maintenance,
                'calendar_events': calendar_events,
                'summary': {
                    'total_scheduled_items': len(calendar_events),
                    'critical_items': len([e for e in calendar_events if e['priority'] == 'critical']),
                    'this_week_count': len([e for e in calendar_events if 
                                           datetime.fromisoformat(e['date'].replace('Z', '')) <= 
                                           datetime.utcnow() + timedelta(days=7)]),
                    'overdue_count': overdue['total_overdue']
                },
                'generated_at': datetime.utcnow().isoformat()
            }
        }, 200
    
    def _create_scheduled_task(self, data):
        """Create a new scheduled task"""
        import uuid
        
        task = {
            'task_id': f"T{str(uuid.uuid4())[:8].upper()}",
            'title': data['title'],
            'description': data.get('description', ''),
            'project_id': data.get('project_id'),
            'task_type': data['task_type'],
            'priority': data.get('priority', 'medium'),
            'scheduled_date': data['scheduled_date'],
            'duration_hours': data.get('duration_hours', 1),
            'assigned_to': data.get('assigned_to'),
            'status': 'scheduled',
            'created_at': datetime.utcnow().isoformat(),
            'created_by': data.get('created_by', 'system')
        }
        
        # Handle recurring tasks
        if data.get('recurring', {}).get('enabled'):
            task['recurring'] = data['recurring']
        
        return task


class SchedulerStatsResource(Resource):
    """
    Resource for scheduler statistics and performance metrics
    """
    
    def get(self):
        """
        Get scheduler performance statistics
        """
        try:
            # Mock statistics - in production this would query actual data
            stats = {
                'task_completion_metrics': {
                    'completed_on_time': 85,
                    'completed_late': 12,
                    'cancelled': 3,
                    'average_delay_days': 1.8,
                    'on_time_percentage': 87.6
                },
                'workload_distribution': {
                    'total_active_tasks': 48,
                    'high_priority_tasks': 15,
                    'medium_priority_tasks': 23,
                    'low_priority_tasks': 10,
                    'overdue_tasks': 4
                },
                'resource_utilization': {
                    'survey_teams': {'capacity': 5, 'utilized': 4, 'utilization_rate': 80},
                    'inspection_teams': {'capacity': 8, 'utilized': 6, 'utilization_rate': 75},
                    'maintenance_teams': {'capacity': 12, 'utilized': 9, 'utilization_rate': 75},
                    'testing_teams': {'capacity': 6, 'utilized': 5, 'utilization_rate': 83.3}
                },
                'upcoming_peaks': [
                    {'date': '2024-01-15', 'task_count': 8, 'resource_strain': 'medium'},
                    {'date': '2024-01-22', 'task_count': 12, 'resource_strain': 'high'},
                    {'date': '2024-02-05', 'task_count': 6, 'resource_strain': 'low'}
                ]
            }
            
            return {
                'success': True,
                'data': stats
            }, 200
            
        except Exception as e:
            logger.error(f"Error getting scheduler stats: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500


class TaskResource(Resource):
    """
    Resource for individual task management
    """
    
    def get(self, task_id):
        """Get specific task details"""
        try:
            # Mock task retrieval - in production would query database
            task = {
                'task_id': task_id,
                'title': 'Substation Site Survey',
                'description': 'Comprehensive site survey for new substation location',
                'project_id': 'PG4001',
                'task_type': 'survey',
                'priority': 'high',
                'scheduled_date': datetime.utcnow().isoformat(),
                'duration_hours': 8,
                'assigned_to': 'survey.team@powergrid.com',
                'status': 'in_progress',
                'progress_percentage': 45,
                'location': 'Maharashtra/Mumbai',
                'equipment_required': ['Survey equipment', 'Safety gear', 'GPS devices'],
                'prerequisites': ['Site access clearance', 'Safety briefing completed'],
                'notes': 'Weather conditions favorable. Team arrived on time.',
                'created_at': (datetime.utcnow() - timedelta(days=2)).isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            return {
                'success': True,
                'data': task
            }, 200
            
        except Exception as e:
            logger.error(f"Error getting task details: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500
    
    def put(self, task_id):
        """Update task status or details"""
        try:
            if not request.json:
                return {
                    'success': False,
                    'message': 'No JSON data provided'
                }, 400
            
            data = request.json
            
            # Mock task update - in production would update database
            updated_task = {
                'task_id': task_id,
                'status': data.get('status', 'scheduled'),
                'progress_percentage': data.get('progress_percentage', 0),
                'notes': data.get('notes', ''),
                'updated_at': datetime.utcnow().isoformat(),
                'updated_by': data.get('updated_by', 'system')
            }
            
            # If completing task, add completion timestamp
            if data.get('status') == 'completed':
                updated_task['completed_at'] = datetime.utcnow().isoformat()
                updated_task['progress_percentage'] = 100
            
            return {
                'success': True,
                'data': updated_task,
                'message': f'Task {task_id} updated successfully'
            }, 200
            
        except Exception as e:
            logger.error(f"Error updating task: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500
    
    def delete(self, task_id):
        """Delete or cancel a task"""
        try:
            # Mock task deletion - in production would update database
            return {
                'success': True,
                'message': f'Task {task_id} cancelled successfully'
            }, 200
            
        except Exception as e:
            logger.error(f"Error cancelling task: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500