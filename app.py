from flask import Flask, request, jsonify
from chatbot import Chatbot
from database import Database
from flask_cors import CORS
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)
# Configure CORS to allow requests from your frontend
CORS(app, resources={
    r"/*": {  # Allow all routes
        "origins": ["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

chatbot = Chatbot()
db = Database()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "ok",
        "message": "Legal Rights Chatbot API is running",
        "endpoints": {
            "/api/test": "Test endpoint",
            "/api/chat": "Chat endpoint (POST)",
            "/api/resources": "Get resources (GET)",
            "/api/resources/search": "Search resources (GET)"
        }
    })

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"status": "ok", "message": "API is working!"})

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        user_message = data.get('message', '')
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        response = chatbot.ask_bot(user_message)
        # Generate downloadable links based on the user's query
        resources = generate_resources(user_message)
        return jsonify({
            'response': response,
            'resources': resources
        })
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

def generate_resources(query):
    # Simplified function to generate downloadable links based on the query
    resources = []
    if 'workplace safety' in query.lower():
        resources = [
            {'title': 'Workplace Safety Guide', 'link': 'https://www.canada.ca/en/employment-social-development/services/health-safety/reports/workplace-safety.html'}
        ]
    elif 'discrimination' in query.lower():
        resources = [
            {'title': 'Discrimination Complaint Form', 'link': 'https://www.canada.ca/en/employment-social-development/services/health-safety/reports/workplace-safety.html'}
        ]
    # Add more conditions for other topics as needed
    return resources

@app.route('/api/resources', methods=['GET'])
def get_resources():
    """Get all resources or filter by type"""
    try:
        resource_type = request.args.get('type')
        if resource_type:
            resources = db.get_resources_by_type(resource_type)
        else:
            resources = db.get_all_resources()
        return jsonify(resources)
    except Exception as e:
        logger.error(f"Error getting resources: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/resources/search', methods=['GET'])
def search_resources():
    """Search resources by name or address"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'No search query provided'}), 400
        
        resources = db.search_resources(query)
        return jsonify(resources)
    except Exception as e:
        logger.error(f"Error searching resources: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested URL was not found on the server',
        'available_endpoints': ['/', '/api/test', '/api/chat', '/api/resources', '/api/resources/search']
    }), 404

if __name__ == '__main__':
    print("\n🚀 Starting Legal Rights Chatbot API Server...")
    print("💡 Server running at http://localhost:5001")
    print("\nAvailable endpoints:")
    print("  - GET  /              : API information")
    print("  - GET  /api/test      : Test endpoint")
    print("  - POST /api/chat      : Chat endpoint")
    print("  - GET  /api/resources : Get resources")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True) 