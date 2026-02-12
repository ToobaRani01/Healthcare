# app.py

# --- Imports ---
# Updated: Added send_from_directory to handle image serving
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory 
# Assuming your user/DB management functions are here
from user_db_operations import (
    register_user, get_user_by_email, get_user_by_id, get_user_threads,
    delete_thread, get_thread_by_id
)
from db_manager import setup_database 
# Chat/AI interaction functions
from api_connection import (
    get_gemini_response, initialize_chat_history, get_history, reset_chat_history,
    current_threads
)
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import Markup
from PIL import Image
from datetime import datetime
import os
import markdown 
import traceback # For better error logging

app = Flask(__name__, static_folder='static')
# IMPORTANT: load secret key from env; fall back to insecure default only for dev
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'basi-2024-043') 
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB upload cap

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Allowed image extensions
ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'tif', 
    'webp', 'svg', 'ico', 'heic', 'heif', 'raw', 'cr2', 
    'nef', 'arw', 'dng', 'orf', 'rw2', 'pef'
}


def allowed_file(filename: str) -> bool:
    """Basic extension whitelist for uploads."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Markdown Filter for Rendering ---
def markdown_filter(text):
    """Converts markdown text to HTML and marks it as safe."""
    return Markup(markdown.markdown(text))

app.jinja_env.filters['markdown'] = markdown_filter

# --- Utility Functions ---
def is_logged_in():
    return 'user_id' in session

# --- Routes ---

@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('main_activity'))
    return redirect(url_for('login')) 

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('signup.html', username=username, email=email)
        
        password_hash = generate_password_hash(password)
        
        if register_user(username, email, password_hash):
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login', email=email))
        else:
            flash('Registration failed. The email may already be in use.', 'danger')
            return render_template('signup.html', username=username, email=email)
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = get_user_by_email(email)
        
        if user and check_password_hash(user['password_hash'], password):
            # Login Success
            session['user_id'] = user['id']
            session['username'] = user['username']
            # Initialize or load history
            initialize_chat_history(user['id'], user['username'])
            flash('Login successful.', 'success')
            return redirect(url_for('main_activity'))
        else:
            flash('Invalid email or password.', 'danger')
            return render_template('login.html', email=email)
    
    return render_template('login.html')

@app.route('/main_activity')
def main_activity():
    if not is_logged_in():
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    username = session['username']
    
    # Optional thread switch via query param
    requested_thread_id = request.args.get('thread_id', type=int)

    # Load user's threads for sidebar
    threads = get_user_threads(user_id)

    active_thread_id = requested_thread_id or current_threads.get(user_id)

    # If none selected, default to most recent existing thread (no auto-create)
    if active_thread_id is None and threads:
        active_thread_id = threads[0]['id']

    # Initialize or switch to requested thread; returns active thread id
    active_thread_id = initialize_chat_history(user_id, username, thread_id_to_load=active_thread_id)

    # Refresh history for active thread
    history = get_history(user_id)
    
    return render_template('main.html', username=username, history=history, threads=threads, active_thread_id=active_thread_id)

@app.route('/new_chat', methods=['POST'])
def new_chat():
    if 'user_id' not in session:
        return jsonify({"message": "Authentication required."}), 401
    user_id = session['user_id']
    
    try:
        reset_chat_history(user_id) 
        return jsonify({"message": "New chat started successfully."}), 200
    except Exception as e:
        print(f"Error resetting chat history: {e}")
        return jsonify({"message": "Failed to start a new chat due to a server error."}), 500

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/threads/<int:thread_id>/delete', methods=['POST'])
def delete_thread_route(thread_id):
    if not is_logged_in():
        return jsonify({"message": "Authentication required."}), 401
    user_id = session['user_id']

    # Ensure thread belongs to user
    thread = get_thread_by_id(user_id, thread_id)
    if not thread:
        return jsonify({"message": "Thread not found."}), 404

    if not delete_thread(user_id, thread_id):
        return jsonify({"message": "Failed to delete thread."}), 500

    # Clear current thread selection if it was deleted
    if current_threads.get(user_id) == thread_id:
        current_threads[user_id] = None

    # Pick next available thread, if any
    threads = get_user_threads(user_id)
    next_thread_id = threads[0]['id'] if threads else None

    return jsonify({"message": "Thread deleted.", "next_thread_id": next_thread_id}), 200

# --- NEW ROUTE: Serve uploaded images for the front-end to display ---
@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    """Serves uploaded files directly from the UPLOAD_FOLDER."""
    # Require auth to avoid exposing user uploads publicly
    if not is_logged_in():
        return jsonify({"message": "Authentication required."}), 401
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({"content": "Authentication required. Please log in again."}), 401
    user_id = session['user_id']

    pil_image = None
    file_path = None
    
    try:
        query = request.form.get('query', '').strip()
        
        # --- IMAGE HANDLING LOGIC ---
        image_file = request.files.get('image')
        image_filename = None
        
        if image_file and image_file.filename:
            # Validate filename + extension
            if not allowed_file(image_file.filename):
                return jsonify({"content": "Only image uploads (png/jpg/jpeg/gif) are allowed.", "role": "error_client"}), 400

            # Enforce max content length (Flask rejects above MAX_CONTENT_LENGTH automatically)
            if request.content_length and request.content_length > app.config['MAX_CONTENT_LENGTH']:
                return jsonify({"content": "Image too large. Max 5MB.", "role": "error_client"}), 400

            # 1. Save to disk
            ext = os.path.splitext(image_file.filename)[1]
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            image_filename = f"user_{user_id}_{timestamp}{ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            
            # Save the file stream to disk
            image_file.save(file_path)
            
            # 2. Open the saved file into a PIL object for the API call
            pil_image = Image.open(file_path)
            
        # --- CRITICAL CHECK: ONLY BLOCK IF BOTH ARE MISSING ---
        if not query and not pil_image:
            # Clean up the file if no query was provided
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({"content": "Please enter a query or upload an image.", "role": "error_client"}), 200
        
        # 3. Call the AI function
        ai_message = get_gemini_response(user_id, query, pil_image, image_filename) 

        # 4. Prepare the final JSON response for the frontend
        response_data = {
            "content": ai_message["content"],
            "role": "assistant" 
        }
        
        # Handle API key missing or other critical errors returned by the AI function
        if ai_message.get("metadata", {}).get("status") == "error":
             response_data["role"] = "error_internal" 
             return jsonify(response_data) 
        
        return jsonify(response_data)

    except Exception as e:
        print(f"Server CRITICAL Error during AI interaction: {e}")
        traceback.print_exc() 
        
        error_message = f"An internal server error occurred. (Error: {str(e)})"
        
        return jsonify({"content": error_message, "role": "error"}), 500
    finally:
        # Ensure the PIL image object is closed to release memory
        if pil_image:
            pil_image.close()


# --- Flask Run ---
if __name__ == '__main__':
    setup_database()
    print("Starting Flask application...")
    app.run(debug=True)