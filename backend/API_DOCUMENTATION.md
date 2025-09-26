# PowerGrid ML Backend API Documentation

## Overview

The PowerGrid ML Backend provides a comprehensive RESTful API for managing power grid projects with integrated machine learning capabilities for risk assessment, cost prediction, and timeline forecasting.

## Base URL
```
http://localhost:5000
```

## Authentication
Currently, the API does not require authentication. In production, implement appropriate authentication mechanisms.

## Response Format
All API responses follow this format:
```json
{
  "success": true/false,
  "data": {...},
  "message": "Optional message",
  "timestamp": "ISO timestamp"
}
```

## Error Handling
Error responses include:
- `400`: Bad Request - Invalid request data
- `404`: Not Found - Resource not found
- `405`: Method Not Allowed - HTTP method not supported
- `500`: Internal Server Error - Server-side error

---

## API Endpoints

### 1. Health & System

#### GET /health
Get system health status
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "services": {
    "database": {"status": "connected", "project_count": 150},
    "ml_models": {"status": "loaded", "service_available": true},
    "dataset": {"exists": true, "path": "/path/to/dataset"}
  }
}
```

#### GET /api/endpoints
List all available API endpoints

---

### 2. Predictions

#### POST /api/predictions/calculate
Calculate predictions for a single project

**Request Body:**
```json
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
```

**Response:**
```json
{
  "success": true,
  "data": {
    "predicted_total_cost": 1450.50,
    "predicted_timeline_months": 26.2,
    "cost_overrun_probability": 0.65,
    "delay_probability": 0.72,
    "risk_score": 7.2,
    "risk_category": "High",
    "confidence_score": 0.89,
    "recommendations": [
      "Consider improving vendor reliability",
      "Plan for material procurement delays"
    ]
  }
}
```

#### POST /api/predictions/batch
Calculate predictions for multiple projects

**Request Body:**
```json
{
  "project_ids": ["PG4001", "PG4002", "PG4003"]
}
```

#### GET /api/predictions/models
Get ML model information and performance metrics

#### POST /api/predictions/retrain
Retrain ML models

---

### 3. Projects

#### GET /api/projects
Get all projects with pagination and filtering

**Query Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 50)
- `status`: Filter by status
- `risk`: Filter by risk level
- `project_type`: Filter by project type

#### GET /api/projects/{project_id}
Get specific project details

#### POST /api/projects
Create a new project

**Request Body:**
```json
{
  "name": "New Substation Project",
  "project_type": "substation",
  "location": "Maharashtra/Mumbai",
  "base_estimated_cost": 1500.0,
  "planned_timeline_months": 18,
  "terrain_type": "urban",
  "labour_wage_rate": 450.0
}
```

#### PUT /api/projects/{project_id}
Update an existing project

#### DELETE /api/projects/{project_id}
Delete a project

#### GET /api/projects/stats
Get project statistics and summaries

#### POST /api/projects/search
Search projects with advanced filters

**Request Body:**
```json
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
```

---

### 4. Analytics

#### GET /api/analytics
Get comprehensive analytics dashboard data

#### GET /api/analytics/{type}
Get specific analytics type
- Types: `overview`, `trends`, `performance`, `risk_analysis`, `regional_analysis`

#### POST /api/analytics/export
Export analytics data

**Request Body:**
```json
{
  "export_type": "overview",
  "format": "json|csv",
  "date_range": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }
}
```

---

### 5. Chatbot

#### POST /api/chatbot
Process chatbot message and get AI response

**Request Body:**
```json
{
  "message": "What is the risk assessment for project PG4001?",
  "context": {
    "project_id": "PG4001",
    "user_id": "user123",
    "conversation_id": "conv456"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": "Risk Assessment for Project PG4001...",
    "timestamp": "2024-01-01T00:00:00",
    "context": {...}
  }
}
```

#### GET /api/chatbot/stats
Get chatbot usage statistics

---

### 6. Scheduler

#### GET /api/scheduler
Get comprehensive schedule data

#### GET /api/scheduler/{type}
Get specific schedule type
- Types: `upcoming`, `overdue`, `milestones`, `maintenance`

#### POST /api/scheduler
Create new scheduled task

**Request Body:**
```json
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
```

#### GET /api/scheduler/stats
Get scheduler performance statistics

#### GET /api/scheduler/tasks/{task_id}
Get specific task details

#### PUT /api/scheduler/tasks/{task_id}
Update task status or details

#### DELETE /api/scheduler/tasks/{task_id}
Cancel/delete a task

---

### 7. Geospatial

#### GET /api/geospatial
Get comprehensive geospatial data

#### GET /api/geospatial/{type}
Get specific geospatial data type
- Types: `projects`, `assets`, `network`, `regions`

#### POST /api/geospatial/search
Search geospatial data with filters

**Request Body:**
```json
{
  "search_type": "projects",
  "filters": {
    "region": "Western Region",
    "state": "Maharashtra",
    "project_type": "substation",
    "status": "active",
    "risk_level": "high",
    "radius_km": 50,
    "center_point": {"lat": 19.0760, "lng": 72.8777}
  }
}
```

#### POST /api/geospatial/export
Export geospatial data

**Request Body:**
```json
{
  "export_type": "projects",
  "format": "geojson|csv",
  "filters": {...}
}
```

---

## ML Model Information

### Supported Algorithms
- Random Forest
- XGBoost
- LightGBM
- CatBoost (optional)

### Features Used
- Project type, terrain type, location
- Cost and timeline factors
- Vendor and material reliability
- Historical delay patterns
- Environmental factors

### Predictions Provided
- **Cost Overrun Probability**: Likelihood of budget overrun
- **Delay Probability**: Likelihood of timeline delays
- **Total Cost Prediction**: Estimated final project cost
- **Timeline Prediction**: Estimated project completion time
- **Risk Score**: Overall risk rating (1-10)
- **Risk Category**: High/Medium/Low risk classification

### Model Performance
- Cross-validation accuracy: ~85-90%
- Feature importance analysis available
- Regular model retraining supported

---

## Example Usage

### 1. Create a New Project and Get Predictions
```bash
# Create project
curl -X POST http://localhost:5000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mumbai Substation Expansion",
    "project_type": "substation",
    "location": "Maharashtra/Mumbai",
    "base_estimated_cost": 2500.0,
    "planned_timeline_months": 20
  }'

# Get predictions
curl -X POST http://localhost:5000/api/predictions/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "projectType": "substation",
    "terrainType": "urban",
    "location": "Maharashtra/Mumbai",
    "baseEstimatedCost": 2500.0,
    "plannedTimelineMonths": 20
  }'
```

### 2. Get Analytics Dashboard
```bash
curl http://localhost:5000/api/analytics
```

### 3. Chat with AI Assistant
```bash
curl -X POST http://localhost:5000/api/chatbot \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me high-risk projects in Maharashtra",
    "context": {"user_id": "analyst1"}
  }'
```

---

## Development Setup

1. **Install Dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Set Environment Variables:**
```bash
cp .env.example .env
# Edit .env file with your configuration
```

3. **Run the Application:**
```bash
python app.py
```

4. **Access API:**
- Base URL: http://localhost:5000
- Health Check: http://localhost:5000/health
- API Documentation: http://localhost:5000/api/endpoints

---

## Production Deployment

### Environment Variables
Set these in production:
- `FLASK_DEBUG=False`
- `SECRET_KEY=your-production-secret`
- `DATABASE_URL=your-production-database-url`
- `CORS_ORIGINS=your-frontend-domains`

### Database Migration
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### ML Model Training
The API automatically trains models on startup using the provided dataset. For production, consider:
- Pre-training models with larger datasets
- Setting up model versioning
- Implementing model monitoring

---

## Support

For questions or issues:
1. Check the health endpoint: `/health`
2. Review logs for detailed error information
3. Verify dataset availability and format
4. Ensure all required dependencies are installed