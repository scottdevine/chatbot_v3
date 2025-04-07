import sys
import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

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

UPLOAD_FOLDER = 'uploads'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

@app.route('/upload', methods=['POST'])
def upload():
    """Handles file uploads."""
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    if 'document' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['document']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            with open(filepath, 'r') as f:
                file_content = f.read()
            if filename.endswith('.txt'):
                print(f"Extracted text from {filename}: {file_content[:100]}...")
            else:
                print(f"Skipping non-txt file: {filename}")
        except Exception as e:
            print(f"Error reading file {filename}: {e}")

        try:
            file.save(filepath)
            return jsonify({'message': 'File uploaded successfully'}), 200
        except Exception as e:
            return jsonify({'error': f'Error saving file: {e}'}), 500
    else:
        return jsonify({'error': 'Unknown error'}), 500

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

@app.route('/select_vector_store', methods=['POST'])
def select_vector_store():
    """Handles vector store selection from the frontend."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data received'}), 400

    selected_store = data.get('selected_store')
    if not selected_store:
        return jsonify({'error': 'Missing "selected_store" key in data'}), 400

    print(f"Vector store selection received: {selected_store}")
    # TODO: Store or use the selected vector store: {selected_store}

    return jsonify({'message': 'Selection received'}), 200

if __name__ == '__main__':
    # Note: Debug mode should be False in production
    app.run(debug=True, port=5001) # Using port 5001 to avoid potential conflicts