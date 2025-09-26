"""
Project model for SQLAlchemy database
"""

from datetime import datetime
from database import db
import json

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Project identification
    project_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    
    # Project details
    project_type = db.Column(db.Enum('Substation', 'Overhead Line', 'Underground Cable', name='project_types'), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    terrain = db.Column(db.Enum('Plains', 'Hilly', 'Desert', 'Coastal', 'Urban', 'Mountainous', name='terrain_types'), nullable=False)
    
    # Cost information
    base_cost_cr = db.Column(db.Float, nullable=False)  # Base cost in Crores
    total_cost_cr = db.Column(db.Float)  # Actual total cost
    steel_price_index = db.Column(db.Float, default=100)
    cement_price_index = db.Column(db.Float, default=100)
    labour_wage_rs_per_day = db.Column(db.Float, nullable=False)
    
    # Resource and reliability factors
    vendor_reliability = db.Column(db.Float, nullable=False)  # 0-1 scale
    material_availability_index = db.Column(db.Float, nullable=False)  # 0-1 scale
    skilled_manpower_pct = db.Column(db.Float, nullable=False)  # 0-100 percentage
    demand_supply_pressure = db.Column(db.Enum('Low', 'Medium', 'High', name='pressure_levels'), default='Medium')
    
    # Timeline information
    planned_timeline_months = db.Column(db.Integer, nullable=False)
    timeline_months = db.Column(db.Integer)  # Actual timeline
    start_date = db.Column(db.Date)
    expected_end_date = db.Column(db.Date)
    actual_end_date = db.Column(db.Date)
    
    # Delay information
    regulatory_delay_months = db.Column(db.Float, default=0)
    historical_delay_count = db.Column(db.Integer, default=0)
    delay_months = db.Column(db.Float)  # Actual delays
    
    # Environmental factors
    avg_annual_rainfall_cm = db.Column(db.Float, default=0)
    
    # Project status and progress
    status = db.Column(db.Enum('Planning', 'In Progress', 'Delayed', 'Completed', 'Cancelled', name='project_status'), default='Planning')
    progress = db.Column(db.Float, default=0)  # 0-100 percentage
    risk = db.Column(db.Enum('Low', 'Medium', 'High', name='risk_levels'), default='Medium')
    
    # Cost overrun information
    overrun_pct = db.Column(db.Float)  # Cost overrun percentage
    
    # Team information
    team_size = db.Column(db.Integer, default=0)
    project_manager = db.Column(db.String(200))
    
    # ML Predictions (stored as JSON)
    predictions = db.Column(db.Text)  # JSON string containing predictions
    last_prediction_date = db.Column(db.DateTime)
    
    # Milestones (stored as JSON)
    milestones = db.Column(db.Text)  # JSON string containing milestone data
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100), nullable=False)
    updated_by = db.Column(db.String(100))
    
    # Notes and additional information
    notes = db.Column(db.Text)
    
    def __init__(self, **kwargs):
        super(Project, self).__init__(**kwargs)
        if not self.project_id:
            self.generate_project_id()
    
    def generate_project_id(self):
        """Generate a unique project ID"""
        import time
        timestamp = str(int(time.time()))[-6:]
        self.project_id = f"PG{timestamp}"
    
    def set_predictions(self, predictions_dict):
        """Store predictions as JSON"""
        self.predictions = json.dumps(predictions_dict)
        self.last_prediction_date = datetime.utcnow()
    
    def get_predictions(self):
        """Get predictions as dictionary"""
        if self.predictions:
            return json.loads(self.predictions)
        return {}
    
    def set_milestones(self, milestones_list):
        """Store milestones as JSON"""
        self.milestones = json.dumps(milestones_list)
    
    def get_milestones(self):
        """Get milestones as list"""
        if self.milestones:
            return json.loads(self.milestones)
        return []
    
    def calculate_cost_overrun_pct(self):
        """Calculate cost overrun percentage"""
        if self.total_cost_cr and self.base_cost_cr:
            return ((self.total_cost_cr - self.base_cost_cr) / self.base_cost_cr) * 100
        return 0
    
    def calculate_delay_months(self):
        """Calculate delay in months"""
        if self.timeline_months and self.planned_timeline_months:
            return self.timeline_months - self.planned_timeline_months
        return 0
    
    def to_dict(self):
        """Convert project to dictionary for JSON serialization"""
        predictions = self.get_predictions()
        milestones = self.get_milestones()
        
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'project_type': self.project_type,
            'state': self.state,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'terrain': self.terrain,
            'base_cost_cr': self.base_cost_cr,
            'total_cost_cr': self.total_cost_cr,
            'steel_price_index': self.steel_price_index,
            'cement_price_index': self.cement_price_index,
            'labour_wage_rs_per_day': self.labour_wage_rs_per_day,
            'vendor_reliability': self.vendor_reliability,
            'material_availability_index': self.material_availability_index,
            'skilled_manpower_pct': self.skilled_manpower_pct,
            'demand_supply_pressure': self.demand_supply_pressure,
            'planned_timeline_months': self.planned_timeline_months,
            'timeline_months': self.timeline_months,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'expected_end_date': self.expected_end_date.isoformat() if self.expected_end_date else None,
            'actual_end_date': self.actual_end_date.isoformat() if self.actual_end_date else None,
            'regulatory_delay_months': self.regulatory_delay_months,
            'historical_delay_count': self.historical_delay_count,
            'delay_months': self.delay_months,
            'avg_annual_rainfall_cm': self.avg_annual_rainfall_cm,
            'status': self.status,
            'progress': self.progress,
            'risk': self.risk,
            'overrun_pct': self.overrun_pct,
            'team_size': self.team_size,
            'project_manager': self.project_manager,
            'predictions': predictions,
            'last_prediction_date': self.last_prediction_date.isoformat() if self.last_prediction_date else None,
            'milestones': milestones,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'notes': self.notes
        }
    
    def to_ml_features(self):
        """Convert project to feature vector for ML model"""
        # Map categorical variables to numerical values
        project_type_map = {'Substation': 0, 'Overhead Line': 1, 'Underground Cable': 2}
        terrain_map = {'Plains': 0, 'Hilly': 1, 'Desert': 2, 'Coastal': 3, 'Urban': 4, 'Mountainous': 5}
        pressure_map = {'Low': 0, 'Medium': 1, 'High': 2}
        
        features = {
            'Project_Type': project_type_map.get(self.project_type, 0),
            'Terrain': terrain_map.get(self.terrain, 0),
            'Base_Cost_Cr': self.base_cost_cr or 0,
            'Steel_Price_Index': self.steel_price_index or 100,
            'Cement_Price_Index': self.cement_price_index or 100,
            'Labour_Wage_RsPerDay': self.labour_wage_rs_per_day or 0,
            'Regulatory_Delay_months': self.regulatory_delay_months or 0,
            'Historical_Delay_Count': self.historical_delay_count or 0,
            'Avg_Annual_Rainfall_cm': self.avg_annual_rainfall_cm or 0,
            'Vendor_Reliability': self.vendor_reliability or 0.5,
            'Material_Availability_Index': self.material_availability_index or 0.5,
            'Demand_Supply_Pressure': pressure_map.get(self.demand_supply_pressure, 1),
            'Skilled_Manpower_pct': self.skilled_manpower_pct or 50,
            'Planned_Timeline_months': self.planned_timeline_months or 12
        }
        
        return features
    
    def __repr__(self):
        return f'<Project {self.project_id}: {self.name}>'