"""
API endpoints for chatbot functionality
"""

from flask import request, jsonify
from flask_restful import Resource
from datetime import datetime
import logging
import json
from models.project_model import Project
from services.prediction_service import PredictionService

logger = logging.getLogger(__name__)

class ChatbotResource(Resource):
    """
    Resource for handling chatbot conversations and AI assistant
    """
    
    def __init__(self):
        self.prediction_service = PredictionService()
    
    def post(self):
        """
        Process chatbot message and generate response
        
        Expected JSON format:
        {
            "message": "What is the risk assessment for project PG4001?",
            "context": {
                "project_id": "PG4001",
                "user_id": "user123",
                "conversation_id": "conv456"
            }
        }
        """
        try:
            if not request.json or 'message' not in request.json:
                return {
                    'success': False,
                    'message': 'Message is required'
                }, 400
            
            user_message = request.json['message']
            context = request.json.get('context', {})
            
            # Process the message and generate response
            response = self._process_message(user_message, context)
            
            # Log the conversation
            self._log_conversation(user_message, response, context)
            
            return {
                'success': True,
                'data': {
                    'response': response,
                    'timestamp': datetime.utcnow().isoformat(),
                    'context': context
                }
            }, 200
            
        except Exception as e:
            logger.error(f"Error processing chatbot message: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500
    
    def _process_message(self, message, context):
        """
        Process user message and generate appropriate response
        """
        message_lower = message.lower()
        
        # Intent detection and response generation
        if 'risk' in message_lower and 'assessment' in message_lower:
            return self._handle_risk_assessment_query(message, context)
        
        elif 'predict' in message_lower or 'forecast' in message_lower:
            return self._handle_prediction_query(message, context)
        
        elif 'project' in message_lower and ('status' in message_lower or 'information' in message_lower):
            return self._handle_project_info_query(message, context)
        
        elif 'cost' in message_lower and ('estimate' in message_lower or 'budget' in message_lower):
            return self._handle_cost_query(message, context)
        
        elif 'timeline' in message_lower or 'schedule' in message_lower:
            return self._handle_timeline_query(message, context)
        
        elif 'recommendation' in message_lower or 'suggest' in message_lower:
            return self._handle_recommendation_query(message, context)
        
        elif 'analytics' in message_lower or 'dashboard' in message_lower or 'statistics' in message_lower:
            return self._handle_analytics_query(message, context)
        
        elif any(greeting in message_lower for greeting in ['hello', 'hi', 'hey', 'help']):
            return self._handle_greeting()
        
        else:
            return self._handle_general_query(message, context)
    
    def _handle_risk_assessment_query(self, message, context):
        """Handle risk assessment related queries"""
        project_id = context.get('project_id') or self._extract_project_id(message)
        
        if project_id:
            try:
                project = Project.query.filter_by(project_id=project_id).first()
                if not project:
                    return f"I couldn't find project {project_id}. Please check the project ID and try again."
                
                predictions = project.get_predictions()
                if predictions:
                    risk_score = predictions.get('risk_score', 0)
                    risk_category = predictions.get('risk_category', 'Unknown')
                    confidence = predictions.get('confidence_score', 0)
                    
                    response = f"Risk Assessment for Project {project_id} ({project.name}):\n\n"
                    response += f"• Risk Level: {risk_category}\n"
                    response += f"• Risk Score: {risk_score:.2f}/10\n"
                    response += f"• Confidence Level: {confidence:.1%}\n\n"
                    
                    if 'cost_overrun_probability' in predictions:
                        response += f"• Cost Overrun Probability: {predictions['cost_overrun_probability']:.1%}\n"
                    
                    if 'delay_probability' in predictions:
                        response += f"• Delay Probability: {predictions['delay_probability']:.1%}\n"
                    
                    if 'predicted_delay_months' in predictions:
                        response += f"• Predicted Delay: {predictions['predicted_delay_months']:.1f} months\n"
                    
                    # Add key risk factors
                    if project.vendor_reliability_score < 0.6:
                        response += f"\n⚠️ Key Risk Factor: Low vendor reliability ({project.vendor_reliability_score:.1%})"
                    
                    if project.material_availability_index < 0.7:
                        response += f"\n⚠️ Key Risk Factor: Limited material availability ({project.material_availability_index:.1%})"
                    
                    return response
                
                else:
                    return f"No risk assessment predictions available for project {project_id}. Would you like me to generate one?"
                    
            except Exception as e:
                logger.error(f"Error getting risk assessment: {str(e)}")
                return "I encountered an error while retrieving the risk assessment. Please try again."
        
        else:
            return "Please specify which project you'd like a risk assessment for. You can provide the project ID or name."
    
    def _handle_prediction_query(self, message, context):
        """Handle prediction related queries"""
        project_id = context.get('project_id') or self._extract_project_id(message)
        
        if project_id:
            try:
                project = Project.query.filter_by(project_id=project_id).first()
                if not project:
                    return f"Project {project_id} not found. Please check the project ID."
                
                # Generate new predictions
                project_data = project.to_ml_features()
                predictions = self.prediction_service.predict_project_outcomes(project_data)
                
                response = f"Predictions for Project {project_id} ({project.name}):\n\n"
                
                if 'predicted_total_cost' in predictions:
                    response += f"• Predicted Total Cost: ₹{predictions['predicted_total_cost']:,.0f}\n"
                
                if 'predicted_timeline_months' in predictions:
                    response += f"• Predicted Timeline: {predictions['predicted_timeline_months']:.1f} months\n"
                
                if 'cost_overrun_probability' in predictions:
                    response += f"• Cost Overrun Risk: {predictions['cost_overrun_probability']:.1%}\n"
                
                if 'delay_probability' in predictions:
                    response += f"• Delay Risk: {predictions['delay_probability']:.1%}\n"
                
                # Add recommendations
                if 'recommendations' in predictions:
                    response += "\n📋 Key Recommendations:\n"
                    for rec in predictions['recommendations'][:3]:  # Top 3 recommendations
                        response += f"• {rec}\n"
                
                return response
                
            except Exception as e:
                logger.error(f"Error generating predictions: {str(e)}")
                return "I encountered an error while generating predictions. Please try again."
        
        else:
            return "Please specify which project you'd like predictions for. You can provide the project ID or name."
    
    def _handle_project_info_query(self, message, context):
        """Handle project information queries"""
        project_id = context.get('project_id') or self._extract_project_id(message)
        
        if project_id:
            try:
                project = Project.query.filter_by(project_id=project_id).first()
                if not project:
                    return f"Project {project_id} not found."
                
                response = f"Project Information - {project_id}:\n\n"
                response += f"• Name: {project.name}\n"
                response += f"• Type: {project.project_type}\n"
                response += f"• Location: {project.location}\n"
                response += f"• Status: {project.status}\n"
                response += f"• Estimated Cost: ₹{project.base_estimated_cost:,.0f}\n"
                response += f"• Planned Timeline: {project.planned_timeline_months} months\n"
                response += f"• Terrain: {project.terrain_type}\n"
                
                if project.risk:
                    response += f"• Risk Level: {project.risk}\n"
                
                if project.created_at:
                    response += f"• Created: {project.created_at.strftime('%Y-%m-%d')}\n"
                
                return response
                
            except Exception as e:
                logger.error(f"Error getting project info: {str(e)}")
                return "I encountered an error while retrieving project information."
        
        else:
            # List recent projects
            try:
                recent_projects = Project.query.order_by(Project.created_at.desc()).limit(10).all()
                if recent_projects:
                    response = "Here are the most recent projects:\n\n"
                    for project in recent_projects:
                        response += f"• {project.project_id}: {project.name} ({project.status})\n"
                    response += "\nYou can ask for details about any specific project by providing its ID."
                    return response
                else:
                    return "No projects found in the system."
                    
            except Exception as e:
                return "I encountered an error while retrieving project list."
    
    def _handle_cost_query(self, message, context):
        """Handle cost-related queries"""
        project_id = context.get('project_id') or self._extract_project_id(message)
        
        if project_id:
            try:
                project = Project.query.filter_by(project_id=project_id).first()
                if not project:
                    return f"Project {project_id} not found."
                
                response = f"Cost Information for {project_id}:\n\n"
                response += f"• Base Estimated Cost: ₹{project.base_estimated_cost:,.0f}\n"
                
                predictions = project.get_predictions()
                if predictions:
                    if 'predicted_total_cost' in predictions:
                        predicted_cost = predictions['predicted_total_cost']
                        variance = predicted_cost - project.base_estimated_cost
                        variance_pct = (variance / project.base_estimated_cost) * 100
                        
                        response += f"• Predicted Total Cost: ₹{predicted_cost:,.0f}\n"
                        response += f"• Cost Variance: ₹{variance:,.0f} ({variance_pct:+.1f}%)\n"
                    
                    if 'cost_overrun_probability' in predictions:
                        response += f"• Cost Overrun Risk: {predictions['cost_overrun_probability']:.1%}\n"
                
                # Add cost factors
                response += f"\n📊 Cost Factors:\n"
                response += f"• Labour Wage Rate: ₹{project.labour_wage_rate}/day\n"
                response += f"• Steel Price Index: {project.steel_price_index}\n"
                response += f"• Cement Price Index: {project.cement_price_index}\n"
                
                return response
                
            except Exception as e:
                logger.error(f"Error getting cost info: {str(e)}")
                return "I encountered an error while retrieving cost information."
        
        else:
            return "Please specify which project you'd like cost information for."
    
    def _handle_timeline_query(self, message, context):
        """Handle timeline-related queries"""
        project_id = context.get('project_id') or self._extract_project_id(message)
        
        if project_id:
            try:
                project = Project.query.filter_by(project_id=project_id).first()
                if not project:
                    return f"Project {project_id} not found."
                
                response = f"Timeline Information for {project_id}:\n\n"
                response += f"• Planned Timeline: {project.planned_timeline_months} months\n"
                
                predictions = project.get_predictions()
                if predictions:
                    if 'predicted_timeline_months' in predictions:
                        predicted_timeline = predictions['predicted_timeline_months']
                        delay = predicted_timeline - project.planned_timeline_months
                        
                        response += f"• Predicted Timeline: {predicted_timeline:.1f} months\n"
                        response += f"• Expected Delay: {delay:.1f} months\n"
                    
                    if 'delay_probability' in predictions:
                        response += f"• Delay Probability: {predictions['delay_probability']:.1%}\n"
                
                # Add timeline factors
                response += f"\n📅 Timeline Factors:\n"
                response += f"• Regulatory Delay Estimate: {project.regulatory_delay_estimate} months\n"
                response += f"• Historical Delay Pattern: {project.historical_delay_pattern}\n"
                response += f"• Skilled Manpower Availability: {project.skilled_manpower_availability}%\n"
                
                return response
                
            except Exception as e:
                logger.error(f"Error getting timeline info: {str(e)}")
                return "I encountered an error while retrieving timeline information."
        
        else:
            return "Please specify which project you'd like timeline information for."
    
    def _handle_recommendation_query(self, message, context):
        """Handle recommendation queries"""
        project_id = context.get('project_id') or self._extract_project_id(message)
        
        if project_id:
            try:
                project = Project.query.filter_by(project_id=project_id).first()
                if not project:
                    return f"Project {project_id} not found."
                
                # Generate recommendations
                project_data = project.to_ml_features()
                predictions = self.prediction_service.predict_project_outcomes(project_data)
                
                response = f"Recommendations for Project {project_id}:\n\n"
                
                if 'recommendations' in predictions:
                    for i, rec in enumerate(predictions['recommendations'], 1):
                        response += f"{i}. {rec}\n"
                else:
                    # Generate basic recommendations based on project data
                    recommendations = []
                    
                    if project.vendor_reliability_score < 0.7:
                        recommendations.append("Consider reviewing vendor selection due to low reliability score")
                    
                    if project.material_availability_index < 0.8:
                        recommendations.append("Ensure material procurement planning due to availability concerns")
                    
                    if project.skilled_manpower_availability < 70:
                        recommendations.append("Plan for additional manpower training or recruitment")
                    
                    if project.regulatory_delay_estimate > 2:
                        recommendations.append("Engage early with regulatory authorities to minimize delays")
                    
                    for i, rec in enumerate(recommendations, 1):
                        response += f"{i}. {rec}\n"
                
                return response if response.strip().endswith('.') or response.strip().endswith(':') else response + "\nWould you like more specific recommendations for any area?"
                
            except Exception as e:
                logger.error(f"Error generating recommendations: {str(e)}")
                return "I encountered an error while generating recommendations."
        
        else:
            return "Please specify which project you'd like recommendations for."
    
    def _handle_analytics_query(self, message, context):
        """Handle analytics and dashboard queries"""
        try:
            from app import db
            from sqlalchemy import func
            
            # Get basic statistics
            total_projects = Project.query.count()
            active_projects = Project.query.filter(Project.status.in_(['Planning', 'In Progress'])).count()
            high_risk_projects = Project.query.filter(Project.risk == 'High').count()
            
            response = f"📊 PowerGrid Analytics Overview:\n\n"
            response += f"• Total Projects: {total_projects}\n"
            response += f"• Active Projects: {active_projects}\n"
            response += f"• High Risk Projects: {high_risk_projects}\n"
            
            # Portfolio value
            total_value = db.session.query(func.sum(Project.base_estimated_cost)).scalar() or 0
            response += f"• Total Portfolio Value: ₹{total_value:,.0f}\n"
            
            # Recent high-risk projects
            recent_high_risk = Project.query.filter(Project.risk == 'High').limit(3).all()
            if recent_high_risk:
                response += f"\n⚠️ High Risk Projects Needing Attention:\n"
                for project in recent_high_risk:
                    response += f"• {project.project_id}: {project.name}\n"
            
            response += "\nWould you like detailed analytics for any specific area (risk, cost, timeline, regional)?"
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return "I encountered an error while retrieving analytics data."
    
    def _handle_greeting(self):
        """Handle greeting messages"""
        return """Hello! I'm your PowerGrid AI Assistant. I can help you with:

🔍 Project Information - Ask about specific projects
📊 Risk Assessments - Get risk analysis for any project  
📈 Predictions - Generate cost and timeline forecasts
💰 Cost Analysis - Detailed cost breakdowns and estimates
📅 Timeline Analysis - Schedule and delay predictions
📋 Recommendations - Get actionable insights
📊 Analytics - Portfolio statistics and dashboards

Just ask me about any project using its ID, or ask general questions like:
• "What's the risk assessment for project PG4001?"
• "Show me analytics for all projects"
• "Give me recommendations for project XYZ"

How can I help you today?"""
    
    def _handle_general_query(self, message, context):
        """Handle general queries that don't match specific intents"""
        return """I'm here to help with PowerGrid project management and analysis. I can assist with:

• Project information and status
• Risk assessments and predictions
• Cost and timeline analysis
• Recommendations and insights
• Analytics and reporting

Please try asking me about:
• Specific project details (provide project ID)
• Risk assessment for a project
• Cost predictions or timeline forecasts
• Overall portfolio analytics

Is there something specific you'd like to know about your projects?"""
    
    def _extract_project_id(self, message):
        """Extract project ID from message text"""
        import re
        
        # Look for patterns like PG4001, PG-4001, etc.
        pattern = r'\b[Pp][Gg][-]?(\d{4,5})\b'
        match = re.search(pattern, message)
        if match:
            return f"PG{match.group(1)}"
        
        # Look for generic project patterns
        pattern = r'\bproject\s+([A-Z0-9]{5,10})\b'
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        
        return None
    
    def _log_conversation(self, user_message, bot_response, context):
        """Log conversation for analytics and improvement"""
        try:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'user_message': user_message,
                'bot_response': bot_response,
                'context': context,
                'message_length': len(user_message),
                'response_length': len(bot_response)
            }
            
            # In production, this would be stored in a database or logging service
            logger.info(f"Chatbot conversation: {json.dumps(log_entry)}")
            
        except Exception as e:
            logger.error(f"Error logging conversation: {str(e)}")


class ChatbotStatsResource(Resource):
    """
    Resource for chatbot usage statistics
    """
    
    def get(self):
        """
        Get chatbot usage statistics
        """
        try:
            # In a production system, this would query actual conversation logs
            # For now, return mock statistics
            
            stats = {
                'total_conversations': 150,
                'active_users': 25,
                'average_messages_per_conversation': 4.2,
                'top_queries': [
                    {'query_type': 'risk_assessment', 'count': 45},
                    {'query_type': 'project_info', 'count': 38},
                    {'query_type': 'predictions', 'count': 32},
                    {'query_type': 'analytics', 'count': 20},
                    {'query_type': 'recommendations', 'count': 15}
                ],
                'user_satisfaction': 4.6,  # out of 5
                'response_accuracy': 89.5  # percentage
            }
            
            return {
                'success': True,
                'data': stats
            }, 200
            
        except Exception as e:
            logger.error(f"Error getting chatbot stats: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500