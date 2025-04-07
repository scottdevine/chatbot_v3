import sys
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
import dotenv
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

login_manager = LoginManager()
app = Flask(__name__)
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def get(user_id):
        # In a real application, this would fetch the user from a database
        return None

@login_manager.user_loader
def load_user(user_id):
    # In a real application, this would fetch the user from a database
    return User()

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

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", 'uploads')
# In-memory user store (insecure for production!)
users = {'testuser': {'password': 'password'}}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize conversation history
conversation_history = []

# Initialize the CentralAgent (consider if it should be initialized per request or once)
# For simplicity, initializing once here. If state needs to be reset, initialize per request.
try:
    central_agent = CentralAgent(vector_store_type=app.config.get('VECTOR_STORE_TYPE', 'in-memory'))
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
            file.save(filepath)
            # Add document to vector store
            try:
                central_agent.orchestrator.execute_tools(["VectorStore"], {"file_path": filepath, "add": True})
            except Exception as e:
                print(f"Error adding document to vector store: {e}")
                return jsonify({'error': f'Error adding document to vector store: {e}'}), 500
            return jsonify({'message': 'File uploaded and added to vector store successfully', 'filename': filename}), 200
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

@app.route('/api/vector_store/documents', methods=['GET'])
def get_vector_store_documents():
    """Retrieves a list of documents from the vector store."""
    if not central_agent:
        return jsonify({"error": "Chatbot agent not initialized"}), 500
    try:
        documents = central_agent.get_documents()
        return jsonify({"documents": documents}), 200
    except Exception as e:
        print(f"Error retrieving documents: {e}")
        return jsonify({"error": f"Error retrieving documents: {e}"}), 500

@app.route('/api/vector_store/documents/<doc_id>', methods=['DELETE'])
def delete_vector_store_document(doc_id):
    """Deletes a document from the vector store."""
    if not central_agent or not central_agent.orchestrator.collection:
        return jsonify({"error": "Chatbot agent or collection not initialized"}), 500
    try:
        central_agent.orchestrator.collection.delete(ids=[doc_id])
        return jsonify({"message": "Document deleted successfully"}), 200
    except Exception as e:
        print(f"Error deleting document: {e}")
        return jsonify({"error": "Failed to delete document"}), 500
def delete_vector_store_document(doc_id):
    """Deletes a document from the vector store."""
    if not central_agent:
        return jsonify({"error": "Chatbot agent not initialized"}), 500
    try:
        central_agent.delete_document(doc_id)
        return jsonify({"message": f"Document {doc_id} deleted successfully"}), 200
    except Exception as e:
        print(f"Error deleting document: {e}")
        return jsonify({"error": f"Error deleting document: {e}"}), 500

@app.route('/api/vector_store/status', methods=['GET'])
def get_vector_store_status():
    """Retrieves the status of the vector store."""
    if not central_agent or not central_agent.orchestrator.collection:
        return jsonify({"error": "Chatbot agent or collection not initialized"}), 500
    try:
        count = central_agent.orchestrator.collection.count()
        return jsonify({"status": {"document_count": count}}), 200
    except Exception as e:
        print(f"Error getting vector store status: {e}")
        return jsonify({"error": "Failed to get vector store status"}), 500
def get_vector_store_status():
    """Retrieves the status of the vector store."""
    if not central_agent:
        return jsonify({"error": "Chatbot agent not initialized"}), 500
    try:
        status = central_agent.get_vector_store_status()
        return jsonify({"status": status}), 200
    except Exception as e:
        print(f"Error getting vector store status: {e}")
        return jsonify({"error": f"Error getting vector store status: {e}"}), 500

@app.route('/list_documents', methods=['GET'])
def list_documents():
    """Lists the documents in the upload folder."""
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        return jsonify({'documents': [], 'message': 'Upload directory not found.'})
    try:
        filenames = os.listdir(upload_folder)
        return jsonify({'documents': filenames})
    except OSError:
        return jsonify({'error': 'Could not list directory contents.'}), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Placeholder for retrieving settings."""
    return jsonify({"message": "Settings endpoint not implemented yet"}), 200

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Placeholder for updating settings."""
    return jsonify({"message": "Settings endpoint not implemented yet"}), 200

if __name__ == '__main__':
    # Note: Debug mode should be False in production
    app.run(debug=True, port=5001) # Using port 5001 to avoid potential conflicts