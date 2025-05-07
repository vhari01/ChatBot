from flask import Flask, render_template, request, jsonify, send_file
from chatbot import Chatbot, TOPIC_SUGGESTIONS
from database import Database
import json
import os
import webbrowser
from threading import Timer

app = Flask(__name__)
chatbot = Chatbot()
db = Database()

def open_browser():
    webbrowser.open('http://localhost:5000')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    response = chatbot.ask_bot(user_message)
    return jsonify({'response': response})

@app.route('/topics', methods=['GET'])
def get_topics():
    return jsonify({'topics': TOPIC_SUGGESTIONS})

@app.route('/map')
def show_map():
    map_file = os.path.join('templates', 'map.html')
    if os.path.exists(map_file):
        return send_file(map_file)
    return "Map not found", 404

# Resource Management Endpoints
@app.route('/resources', methods=['GET'])
def get_resources():
    """Get all resources or filter by type"""
    resource_type = request.args.get('type')
    if resource_type:
        resources = db.get_resources_by_type(resource_type)
    else:
        resources = db.get_all_resources()
    return jsonify(resources)

@app.route('/resources', methods=['POST'])
def add_resource():
    """Add a new resource"""
    resource = request.json
    if not resource:
        return jsonify({'error': 'No resource data provided'}), 400
    
    resource_id = db.add_resource(resource)
    return jsonify({'id': resource_id, 'message': 'Resource added successfully'})

@app.route('/resources/<int:resource_id>', methods=['PUT'])
def update_resource(resource_id):
    """Update an existing resource"""
    resource = request.json
    if not resource:
        return jsonify({'error': 'No resource data provided'}), 400
    
    success = db.update_resource(resource_id, resource)
    if success:
        return jsonify({'message': 'Resource updated successfully'})
    return jsonify({'error': 'Failed to update resource'}), 400

@app.route('/resources/<int:resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    """Delete a resource"""
    success = db.delete_resource(resource_id)
    if success:
        return jsonify({'message': 'Resource deleted successfully'})
    return jsonify({'error': 'Failed to delete resource'}), 400

@app.route('/resources/search', methods=['GET'])
def search_resources():
    """Search resources by name or address"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
    
    resources = db.search_resources(query)
    return jsonify(resources)

if __name__ == '__main__':
    print("\n🚀 Starting Canadian Rights Chatbot...")
    print("📱 Opening web interface in your browser...")
    print("💡 You can ask questions about legal resources and locations")
    print("🌐 If the browser doesn't open automatically, visit: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Open browser after a short delay
    Timer(1.5, open_browser).start()
    
    # Run the app
    app.run(debug=True) 