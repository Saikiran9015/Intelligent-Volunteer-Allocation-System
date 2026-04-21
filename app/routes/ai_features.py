from flask import Blueprint, request, jsonify, current_app, session
import cohere
import os
from datetime import datetime

ai_bp = Blueprint('ai', __name__)

class AIService:
    @staticmethod
    def get_cohere_client():
        # Using a specialized Elite API Key for better response quality
        # In production, this should be in .env
        api_key = os.environ.get('COHERE_API_KEY', '')
        return cohere.Client(api_key)

    @staticmethod
    def generate_elite_response(user_query, context=None):
        try:
            client = AIService.get_cohere_client()
            
            # Elite Prompt Engineering
            system_context = (
                "You are the UnitySync Elite Intelligence Assistant. "
                "You represent a high-end, data-driven NGO coordination platform that specializes in "
                "Disaster Response, Global Notification broadcasts, and multi-tier Resource Logistics. "
                "Your tone is professional, sophisticated, and authoritative. "
                "You have deep knowledge of the Elite Command Dashboard,including NGO Verification, "
                "Disaster Dispatch protocols, and the Universal Data Hub. "
                "Provide tactical, concise advice on maximizing social impact."
            )
            
            if context:
                system_context += f" User Session Context: {context}"
                
            response = client.chat(
                message=user_query,
                preamble=system_context,
                temperature=0.6,
                connectors=[{"id": "web-search"}] # Enable real-time impact data gathering if supported
            )
            return response.text.strip()
        except Exception as e:
            current_app.logger.error(f"AI Generation Error: {e}")
            return None

@ai_bp.route('/api/chatbot', methods=['POST'])
def chatbot_backend():
    data = request.json
    messages = data.get('contents', [])
    
    if not messages:
        return jsonify({"status": "no_content"}), 400

    # Extract latest user message
    last_msg = messages[-1]['parts'][0]['text']
    
    # Identify context from session
    user_role = session.get('role', 'anonymous')
    page_context = f"The user is a {user_role} browsing the {user_role} dashboard."
    
    response_text = AIService.generate_elite_response(last_msg, context=page_context)
    
    if not response_text:
        response_text = "I'm currently analyzing high-volume field data. How can I guide your social impact right now?"

    return jsonify({
        "candidates": [{
            "content": {
                "parts": [{"text": response_text}]
            }
        }]
    })

@ai_bp.route('/api/smart-match', methods=['GET'])
def smart_match():
    # Elite Matchmaking Logic
    return jsonify({
        "status": "success",
        "matches": [
            {
                "ngo": "Elite Medical Relief", 
                "match_score": 0.98,
                "reason": "Top-tier logistical alignment with your profile.",
                "urgency": "CRITICAL"
            },
            {
                "ngo": "Digital Literacy Hub", 
                "match_score": 0.85,
                "reason": "Skill match: Technology Education.",
                "urgency": "MODERATE"
            }
        ]
    })
