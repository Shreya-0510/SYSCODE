"""
Analytics model for storing aggregated analytics and dashboard data
"""

from datetime import datetime
from database import db
import json

class Analytics(db.Model):
    __tablename__ = 'analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Analytics metadata
    analytics_type = db.Column(db.Enum('daily', 'weekly', 'monthly', 'yearly', name='analytics_types'), nullable=False)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    
    # Project metrics
    total_projects = db.Column(db.Integer, default=0)
    active_projects = db.Column(db.Integer, default=0)
    completed_projects = db.Column(db.Integer, default=0)
    delayed_projects = db.Column(db.Integer, default=0)
    cancelled_projects = db.Column(db.Integer, default=0)
    
    # Financial metrics
    total_budget_cr = db.Column(db.Float, default=0)
    total_actual_cost_cr = db.Column(db.Float, default=0)
    avg_cost_overrun_pct = db.Column(db.Float, default=0)
    total_cost_overrun_cr = db.Column(db.Float, default=0)
    
    # Timeline metrics
    avg_project_duration_months = db.Column(db.Float, default=0)
    avg_delay_months = db.Column(db.Float, default=0)
    on_time_projects = db.Column(db.Integer, default=0)
    
    # Risk metrics
    high_risk_projects = db.Column(db.Integer, default=0)
    medium_risk_projects = db.Column(db.Integer, default=0)
    low_risk_projects = db.Column(db.Integer, default=0)
    
    # Progress metrics
    avg_progress_pct = db.Column(db.Float, default=0)
    
    # Detailed breakdowns (stored as JSON)
    regional_breakdown = db.Column(db.Text)  # JSON: [{'region': 'x', 'projects': n, ...}]
    project_type_breakdown = db.Column(db.Text)  # JSON: [{'type': 'x', 'count': n, ...}]
    monthly_trends = db.Column(db.Text)  # JSON: [{'month': 'x', 'metrics': {...}}]
    cost_distribution = db.Column(db.Text)  # JSON: cost brackets and counts
    
    # Predictions and insights
    predicted_completions = db.Column(db.Integer, default=0)  # Next period
    risk_trend = db.Column(db.String(50))  # 'increasing', 'stable', 'decreasing'
    cost_trend = db.Column(db.String(50))
    timeline_trend = db.Column(db.String(50))
    
    # ML model performance metrics
    prediction_accuracy = db.Column(db.Float)  # 0-100 percentage
    model_confidence = db.Column(db.Float)  # 0-100 percentage
    
    # Timestamps
    generated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_regional_breakdown(self, breakdown_list):
        """Store regional breakdown as JSON"""
        self.regional_breakdown = json.dumps(breakdown_list)
    
    def get_regional_breakdown(self):
        """Get regional breakdown as list"""
        if self.regional_breakdown:
            return json.loads(self.regional_breakdown)
        return []
    
    def set_project_type_breakdown(self, breakdown_list):
        """Store project type breakdown as JSON"""
        self.project_type_breakdown = json.dumps(breakdown_list)
    
    def get_project_type_breakdown(self):
        """Get project type breakdown as list"""
        if self.project_type_breakdown:
            return json.loads(self.project_type_breakdown)
        return []
    
    def set_monthly_trends(self, trends_list):
        """Store monthly trends as JSON"""
        self.monthly_trends = json.dumps(trends_list)
    
    def get_monthly_trends(self):
        """Get monthly trends as list"""
        if self.monthly_trends:
            return json.loads(self.monthly_trends)
        return []
    
    def set_cost_distribution(self, distribution_dict):
        """Store cost distribution as JSON"""
        self.cost_distribution = json.dumps(distribution_dict)
    
    def get_cost_distribution(self):
        """Get cost distribution as dictionary"""
        if self.cost_distribution:
            return json.loads(self.cost_distribution)
        return {}
    
    def calculate_completion_rate(self):
        """Calculate project completion rate"""
        if self.total_projects > 0:
            return (self.completed_projects / self.total_projects) * 100
        return 0
    
    def calculate_success_rate(self):
        """Calculate success rate (completed on time and on budget)"""
        if self.total_projects > 0:
            return (self.on_time_projects / self.total_projects) * 100
        return 0
    
    def calculate_cost_efficiency(self):
        """Calculate cost efficiency percentage"""
        if self.total_budget_cr > 0:
            return ((self.total_budget_cr - self.total_cost_overrun_cr) / self.total_budget_cr) * 100
        return 0
    
    @classmethod
    def generate_analytics(cls, projects, period_type='monthly'):
        """Generate analytics from project data"""
        from datetime import date, timedelta
        
        analytics = cls()
        analytics.analytics_type = period_type
        analytics.period_end = date.today()
        
        # Set period start based on type
        if period_type == 'daily':
            analytics.period_start = analytics.period_end
        elif period_type == 'weekly':
            analytics.period_start = analytics.period_end - timedelta(days=7)
        elif period_type == 'monthly':
            analytics.period_start = analytics.period_end - timedelta(days=30)
        else:  # yearly
            analytics.period_start = analytics.period_end - timedelta(days=365)
        
        # Calculate basic metrics
        analytics.total_projects = len(projects)
        analytics.active_projects = len([p for p in projects if p.status == 'In Progress'])
        analytics.completed_projects = len([p for p in projects if p.status == 'Completed'])
        analytics.delayed_projects = len([p for p in projects if p.status == 'Delayed'])
        analytics.cancelled_projects = len([p for p in projects if p.status == 'Cancelled'])
        
        # Financial metrics
        analytics.total_budget_cr = sum(p.base_cost_cr for p in projects if p.base_cost_cr)
        analytics.total_actual_cost_cr = sum(p.total_cost_cr for p in projects if p.total_cost_cr)
        
        cost_overruns = [p.calculate_cost_overrun_pct() for p in projects if p.total_cost_cr]
        if cost_overruns:
            analytics.avg_cost_overrun_pct = sum(cost_overruns) / len(cost_overruns)
        
        analytics.total_cost_overrun_cr = analytics.total_actual_cost_cr - analytics.total_budget_cr
        
        # Timeline metrics
        durations = [p.timeline_months for p in projects if p.timeline_months]
        delays = [p.calculate_delay_months() for p in projects if p.timeline_months and p.planned_timeline_months]
        
        if durations:
            analytics.avg_project_duration_months = sum(durations) / len(durations)
        
        if delays:
            analytics.avg_delay_months = sum(delays) / len(delays)
        
        analytics.on_time_projects = len([p for p in projects if 
                                        p.timeline_months and p.planned_timeline_months and 
                                        p.timeline_months <= p.planned_timeline_months])
        
        # Risk metrics
        analytics.high_risk_projects = len([p for p in projects if p.risk == 'High'])
        analytics.medium_risk_projects = len([p for p in projects if p.risk == 'Medium'])
        analytics.low_risk_projects = len([p for p in projects if p.risk == 'Low'])
        
        # Progress metrics
        progress_values = [p.progress for p in projects if p.progress is not None]
        if progress_values:
            analytics.avg_progress_pct = sum(progress_values) / len(progress_values)
        
        # Generate breakdowns
        analytics._generate_regional_breakdown(projects)
        analytics._generate_project_type_breakdown(projects)
        analytics._generate_cost_distribution(projects)
        
        return analytics
    
    def _generate_regional_breakdown(self, projects):
        """Generate regional breakdown"""
        regional_stats = {}
        
        for project in projects:
            state = project.state
            if state not in regional_stats:
                regional_stats[state] = {
                    'region': state,
                    'project_count': 0,
                    'completed': 0,
                    'total_cost': 0,
                    'avg_progress': 0,
                    'high_risk': 0
                }
            
            stats = regional_stats[state]
            stats['project_count'] += 1
            
            if project.status == 'Completed':
                stats['completed'] += 1
            
            if project.total_cost_cr:
                stats['total_cost'] += project.total_cost_cr
            
            if project.progress:
                stats['avg_progress'] += project.progress
            
            if project.risk == 'High':
                stats['high_risk'] += 1
        
        # Calculate averages
        for state, stats in regional_stats.items():
            if stats['project_count'] > 0:
                stats['completion_rate'] = (stats['completed'] / stats['project_count']) * 100
                stats['avg_cost'] = stats['total_cost'] / stats['project_count']
                stats['avg_progress'] = stats['avg_progress'] / stats['project_count']
        
        self.set_regional_breakdown(list(regional_stats.values()))
    
    def _generate_project_type_breakdown(self, projects):
        """Generate project type breakdown"""
        type_stats = {}
        
        for project in projects:
            ptype = project.project_type
            if ptype not in type_stats:
                type_stats[ptype] = {
                    'type': ptype,
                    'count': 0,
                    'completed': 0,
                    'avg_duration': 0,
                    'avg_cost': 0
                }
            
            stats = type_stats[ptype]
            stats['count'] += 1
            
            if project.status == 'Completed':
                stats['completed'] += 1
            
            if project.timeline_months:
                stats['avg_duration'] += project.timeline_months
            
            if project.total_cost_cr:
                stats['avg_cost'] += project.total_cost_cr
        
        # Calculate averages
        for ptype, stats in type_stats.items():
            if stats['count'] > 0:
                stats['success_rate'] = (stats['completed'] / stats['count']) * 100
                stats['avg_duration'] = stats['avg_duration'] / stats['count']
                stats['avg_cost'] = stats['avg_cost'] / stats['count']
        
        self.set_project_type_breakdown(list(type_stats.values()))
    
    def _generate_cost_distribution(self, projects):
        """Generate cost distribution"""
        cost_brackets = {
            '0-500 Cr': 0,
            '500-1000 Cr': 0,
            '1000-1500 Cr': 0,
            '1500-2000 Cr': 0,
            '2000+ Cr': 0
        }
        
        for project in projects:
            cost = project.base_cost_cr or 0
            
            if cost < 500:
                cost_brackets['0-500 Cr'] += 1
            elif cost < 1000:
                cost_brackets['500-1000 Cr'] += 1
            elif cost < 1500:
                cost_brackets['1000-1500 Cr'] += 1
            elif cost < 2000:
                cost_brackets['1500-2000 Cr'] += 1
            else:
                cost_brackets['2000+ Cr'] += 1
        
        self.set_cost_distribution(cost_brackets)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'analytics_type': self.analytics_type,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'project_metrics': {
                'total_projects': self.total_projects,
                'active_projects': self.active_projects,
                'completed_projects': self.completed_projects,
                'delayed_projects': self.delayed_projects,
                'cancelled_projects': self.cancelled_projects,
                'completion_rate': self.calculate_completion_rate(),
                'success_rate': self.calculate_success_rate()
            },
            'financial_metrics': {
                'total_budget_cr': self.total_budget_cr,
                'total_actual_cost_cr': self.total_actual_cost_cr,
                'avg_cost_overrun_pct': self.avg_cost_overrun_pct,
                'total_cost_overrun_cr': self.total_cost_overrun_cr,
                'cost_efficiency': self.calculate_cost_efficiency()
            },
            'timeline_metrics': {
                'avg_project_duration_months': self.avg_project_duration_months,
                'avg_delay_months': self.avg_delay_months,
                'on_time_projects': self.on_time_projects
            },
            'risk_metrics': {
                'high_risk_projects': self.high_risk_projects,
                'medium_risk_projects': self.medium_risk_projects,
                'low_risk_projects': self.low_risk_projects
            },
            'progress_metrics': {
                'avg_progress_pct': self.avg_progress_pct
            },
            'breakdowns': {
                'regional': self.get_regional_breakdown(),
                'project_type': self.get_project_type_breakdown(),
                'cost_distribution': self.get_cost_distribution()
            },
            'trends': {
                'risk_trend': self.risk_trend,
                'cost_trend': self.cost_trend,
                'timeline_trend': self.timeline_trend
            },
            'ml_metrics': {
                'prediction_accuracy': self.prediction_accuracy,
                'model_confidence': self.model_confidence
            },
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Analytics {self.analytics_type}: {self.period_start} to {self.period_end}>'