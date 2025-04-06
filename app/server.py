import sys
import os
from flask import Flask, request, jsonify, render_template

# Add the project root directory to the Python path
# This allows importing modules from the 'src' directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.central_agent import CentralAgent
except ImportError as e:
    print(f"Error importing CentralAgent: {e}")
    # Provide a fallback or raise an error if CentralAgent is critical
    # For now, we'll let it fail if the import doesn't work.
    # You might need to ensure your PYTHONPATH is set correctly
    # or that the project structure allows this import.
    raise

app = Flask(__name__)

# Initialize conversation history
conversation_history = []

# Initialize the CentralAgent (consider if it should be initialized per request or once)
# For simplicity, initializing once here. If state needs to be reset, initialize per request.
try:
    central_agent = CentralAgent()
except Exception as e:
    print(f"Error initializing CentralAgent: {e}")
    # Handle initialization error appropriately
    central_agent = None # Or raise an error

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handles chat requests."""
    if not central_agent:
        return jsonify({"error": "Chatbot agent not initialized"}), 500

    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' in request body"}), 400

    user_query = data['query']

    try:
        # Process the query using the CentralAgent
        response, sources = central_agent.process_query(user_query)
        tools_used = central_agent.get_used_tools()

        # Append to conversation history
        conversation_history.append((user_query, response))

        return jsonify({"response": response, "sources": sources, "history": conversation_history, "tools": tools_used})
    except Exception as e:
        print(f"Error processing query: {e}")
        # Log the exception traceback for debugging
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An error occurred: {e}"}), 500

if __name__ == '__main__':
    # Note: Debug mode should be False in production
    app.run(debug=True, port=5001) # Using port 5001 to avoid potential conflicts