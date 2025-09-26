"""
Database configuration and initialization
Separate from app.py to avoid circular imports
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize database
db = SQLAlchemy()
migrate = Migrate()

def init_database(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Import models here after db is initialized
    from models.project_model import Project
    from models.regional_data import RegionalData  
    from models.analytics import Analytics
    
    return db