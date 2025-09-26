"""
Regional data model for storing regional information and risk factors
"""

from datetime import datetime
from database import db
import json

class RegionalData(db.Model):
    __tablename__ = 'regional_data'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Location information
    state = db.Column(db.String(100), unique=True, nullable=False, index=True)
    region_code = db.Column(db.String(10), unique=True)
    
    # Geographic information
    center_latitude = db.Column(db.Float)
    center_longitude = db.Column(db.Float)
    boundaries = db.Column(db.Text)  # JSON string of boundary coordinates
    
    # Economic factors
    gdp_index = db.Column(db.Float, default=100)
    industrial_development_index = db.Column(db.Float, default=100)
    infrastructure_quality = db.Column(db.Float, default=5)  # 0-10 scale
    
    # Environmental factors
    average_rainfall = db.Column(db.Float, default=0)
    temperature_min = db.Column(db.Float)
    temperature_max = db.Column(db.Float)
    seismic_risk = db.Column(db.Float, default=1)  # 0-10 scale
    cyclone_risk = db.Column(db.Float, default=1)  # 0-10 scale
    
    # Resource availability
    skilled_labor_availability = db.Column(db.Float, default=50)  # 0-100 percentage
    raw_materials_availability = db.Column(db.Float, default=50)  # 0-100 percentage
    transportation_quality = db.Column(db.Float, default=5)  # 0-10 scale
    connectivity_index = db.Column(db.Float, default=5)  # 0-10 scale
    
    # Regulatory environment
    avg_approval_time_days = db.Column(db.Float, default=60)
    compliance_complexity = db.Column(db.Float, default=5)  # 0-10 scale
    policy_support_level = db.Column(db.Float, default=5)  # 0-10 scale
    
    # Historical project performance
    total_projects = db.Column(db.Integer, default=0)
    completed_projects = db.Column(db.Integer, default=0)
    avg_cost_overrun_pct = db.Column(db.Float, default=0)
    avg_time_overrun_pct = db.Column(db.Float, default=0)
    success_rate_pct = db.Column(db.Float, default=50)
    
    # Risk assessment
    overall_risk = db.Column(db.Enum('Low', 'Medium', 'High', name='risk_levels'), default='Medium')
    terrain_complexity = db.Column(db.Float, default=5)  # 0-10 scale
    weather_risk = db.Column(db.Float, default=5)  # 0-10 scale
    political_stability = db.Column(db.Float, default=5)  # 0-10 scale
    security_concerns = db.Column(db.Float, default=1)  # 0-10 scale
    
    # Market factors
    demand_growth_pct = db.Column(db.Float, default=0)
    competition_level = db.Column(db.Float, default=5)  # 0-10 scale
    price_volatility = db.Column(db.Float, default=5)  # 0-10 scale
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_boundaries(self, boundaries_list):
        """Store boundaries as JSON"""
        self.boundaries = json.dumps(boundaries_list)
    
    def get_boundaries(self):
        """Get boundaries as list"""
        if self.boundaries:
            return json.loads(self.boundaries)
        return []
    
    def calculate_risk_score(self):
        """Calculate overall risk score based on various factors"""
        risk_factors = [
            self.seismic_risk,
            self.cyclone_risk,
            self.weather_risk,
            self.terrain_complexity,
            self.security_concerns,
            (10 - self.political_stability),  # Invert as lower stability = higher risk
            (10 - self.infrastructure_quality),  # Invert
            self.price_volatility,
            self.compliance_complexity
        ]
        
        # Calculate weighted average (0-10 scale)
        weighted_score = sum(risk_factors) / len(risk_factors)
        
        if weighted_score >= 7:
            self.overall_risk = 'High'
        elif weighted_score >= 4:
            self.overall_risk = 'Medium'
        else:
            self.overall_risk = 'Low'
        
        return weighted_score
    
    def update_project_stats(self, projects):
        """Update regional statistics based on projects"""
        state_projects = [p for p in projects if p.state == self.state]
        
        self.total_projects = len(state_projects)
        self.completed_projects = len([p for p in state_projects if p.status == 'Completed'])
        
        if state_projects:
            # Calculate averages
            cost_overruns = [p.calculate_cost_overrun_pct() for p in state_projects if p.total_cost_cr]
            time_overruns = [p.calculate_delay_months() for p in state_projects if p.timeline_months]
            
            if cost_overruns:
                self.avg_cost_overrun_pct = sum(cost_overruns) / len(cost_overruns)
            
            if time_overruns:
                self.avg_time_overrun_pct = sum(time_overruns) / len(time_overruns)
            
            # Success rate calculation
            successful_projects = len([p for p in state_projects if p.status == 'Completed' and 
                                     p.calculate_cost_overrun_pct() < 10 and 
                                     p.calculate_delay_months() < 3])
            
            self.success_rate_pct = (successful_projects / len(state_projects)) * 100 if state_projects else 0
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'state': self.state,
            'region_code': self.region_code,
            'center_latitude': self.center_latitude,
            'center_longitude': self.center_longitude,
            'boundaries': self.get_boundaries(),
            'economic_factors': {
                'gdp_index': self.gdp_index,
                'industrial_development_index': self.industrial_development_index,
                'infrastructure_quality': self.infrastructure_quality
            },
            'environmental_factors': {
                'average_rainfall': self.average_rainfall,
                'temperature_range': {
                    'min': self.temperature_min,
                    'max': self.temperature_max
                },
                'seismic_risk': self.seismic_risk,
                'cyclone_risk': self.cyclone_risk
            },
            'resource_availability': {
                'skilled_labor_availability': self.skilled_labor_availability,
                'raw_materials_availability': self.raw_materials_availability,
                'transportation_quality': self.transportation_quality,
                'connectivity_index': self.connectivity_index
            },
            'regulatory_factors': {
                'avg_approval_time_days': self.avg_approval_time_days,
                'compliance_complexity': self.compliance_complexity,
                'policy_support_level': self.policy_support_level
            },
            'historical_performance': {
                'total_projects': self.total_projects,
                'completed_projects': self.completed_projects,
                'avg_cost_overrun_pct': self.avg_cost_overrun_pct,
                'avg_time_overrun_pct': self.avg_time_overrun_pct,
                'success_rate_pct': self.success_rate_pct
            },
            'risk_factors': {
                'overall_risk': self.overall_risk,
                'terrain_complexity': self.terrain_complexity,
                'weather_risk': self.weather_risk,
                'political_stability': self.political_stability,
                'security_concerns': self.security_concerns
            },
            'market_factors': {
                'demand_growth_pct': self.demand_growth_pct,
                'competition_level': self.competition_level,
                'price_volatility': self.price_volatility
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<RegionalData {self.state}: {self.overall_risk} Risk>'