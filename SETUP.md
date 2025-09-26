# PowerGrid ML Backend Setup Guide

## Prerequisites
- Python 3.13.x (recommended) or Python 3.11+
- Git

## Quick Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Powergrid
```

### 2. Create Virtual Environment
```powershell
# Windows PowerShell
python -m venv powergrid_env

# Activate the virtual environment
& "powergrid_env\Scripts\Activate.ps1"
```

```bash
# macOS/Linux
python -m venv powergrid_env
source powergrid_env/bin/activate
```

### 3. Install Dependencies

#### Option A: Full Installation (Recommended)
```bash
cd backend
pip install -r requirements.txt
```

#### Option B: Core Dependencies Only
```bash
cd backend
pip install -r requirements_core.txt
```

### 4. Run the Backend
```bash
# Make sure virtual environment is activated
cd backend
python app.py
```

The backend will start on `http://localhost:5000`

## API Endpoints

### Health Check
- `GET /health` - Check if the API is running

### Project Management
- `GET /api/projects` - Get all projects
- `POST /api/projects` - Create new project
- `GET /api/projects/<id>` - Get project by ID
- `PUT /api/projects/<id>` - Update project
- `DELETE /api/projects/<id>` - Delete project

### ML Predictions
- `POST /api/predictions/cost` - Predict project cost
- `POST /api/predictions/timeline` - Predict project timeline
- `POST /api/predictions/risk` - Predict project risks
- `POST /api/predictions/comprehensive` - Get all predictions

### Analytics
- `GET /api/analytics/dashboard` - Dashboard summary
- `GET /api/analytics/trends` - Performance trends
- `POST /api/analytics/compare` - Compare projects

### More endpoints available - see API_DOCUMENTATION.md for complete list

## Configuration

Create a `.env` file in the backend directory:
```env
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=sqlite:///instance/powergrid.db
SECRET_KEY=your-secret-key-here
DEBUG=True
```

## Development

### Run Tests
```bash
pytest
```

### Code Formatting
```bash
black .
flake8 .
```

## Production Deployment

For production, use Gunicorn:
```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

## Troubleshooting

### Virtual Environment Issues
- Make sure to activate the virtual environment before running any commands
- If activation fails, try using the batch file: `powergrid_env\Scripts\activate.bat`

### Import Errors
- Ensure all dependencies are installed in the activated virtual environment
- Check that you're running Python commands from within the activated environment

### Database Issues
- The database will be created automatically on first run
- Database file location: `backend/instance/powergrid.db`

## Project Structure
```
Powergrid/
├── backend/                 # Flask ML Backend
│   ├── app.py              # Main application
│   ├── database.py         # Database configuration
│   ├── requirements.txt    # All dependencies
│   ├── requirements_core.txt # Core dependencies
│   ├── api/                # API endpoints
│   ├── models/             # Database models
│   ├── services/           # ML and business logic
│   └── instance/           # Database files
├── frontend/               # React Frontend
├── dataset/               # Training data
└── powergrid_env/         # Virtual environment
```