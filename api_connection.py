# api_connection.py
"""
Main API connection module - orchestrates all components for chat functionality.
This module acts as the main interface while delegating specific tasks to specialized modules.
"""
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import os
import base64
from datetime import datetime
from PIL import Image

# Import modular components
from symptom_detector import is_symptom_query
from response_parser import parse_structured_response
from prompt_builder import build_symptom_prompt, get_non_symptom_message
from api_handler import create_chat_session, send_message, get_gemini_client
from image_analyzer import analyze_medical_image, format_analysis_for_prompt

# Import database operations
from user_db_operations import (
    save_post, save_assistant_post, 
    get_history_by_user_id, create_new_chat_thread, update_thread_title,
    save_structured_response
)

# --- Global In-Memory Stores for Thread Management ---
current_threads = {} 
gemini_chat_sessions = {}
chat_histories = {} 

# Define the UPLOAD_FOLDER path (must match app.py)
UPLOAD_FOLDER = 'uploads' 

# --- Utility Functions ---

def _load_image_base64_from_filename(image_filename):
    """
    Reads a saved image file and returns its content as a Base64 string 
    with MIME type prefix for direct display in HTML (for history).
    """
    if not image_filename:
        return None

    try:
        file_path = os.path.join(UPLOAD_FOLDER, image_filename)
        
        if not os.path.exists(file_path):
            print(f"Warning: Image file not found at {file_path}")
            return None
            
        # Determine MIME type from the file extension
        mime_type = 'image/jpeg' # Default fallback
        if image_filename.lower().endswith('.png'):
            mime_type = 'image/png'
        elif image_filename.lower().endswith('.gif'):
            mime_type = 'image/gif'
        elif image_filename.lower().endswith('.jpg') or image_filename.lower().endswith('.jpeg'):
            mime_type = 'image/jpeg'

        with open(file_path, 'rb') as f:
            base64_data = base64.b64encode(f.read()).decode('utf-8')
            return {
                "base64_data": base64_data,
                "mime_type": mime_type,
                "filename": image_filename
            }
            
    except Exception as e:
        print(f"Error loading image {image_filename} for history: {e}")
        return None

def format_db_record_for_session(record):
    """Converts a database record into a format suitable for Flask session/UI display."""
    
    role_val = record.get('role', 'user') 
    
    # Load image data if filename exists in the record
    image_data = _load_image_base64_from_filename(record.get("image_filename"))

    return {
        "role": role_val,
        "content": record.get("text_content"),
        "image": image_data, 
        "created_at": record["created_at"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(record.get("created_at"), datetime) else str(record.get("created_at")),
        "db_id": record["id"],
        "thread_id": record.get("thread_id") 
    }

def format_history_for_gemini(db_history):
    """
    Formats DB records into Gemini API content objects for chat context. 
    Includes the image part for previous user turns.
    """
    formatted_history = []
    for record in db_history:
        # The model role is 'model' in the API, user role is 'user'
        role = "model" if record['role'] == 'assistant' else "user"
        
        # Construct the parts list for the message
        parts = []
        
        # 1. Add text content (if present)
        if record.get('text_content'):
            parts.append(record['text_content'])
            
        # 2. Add image content for user messages (if present)
        if record.get('image_filename') and role == 'user':
            try:
                file_path = os.path.join(UPLOAD_FOLDER, record['image_filename'])
                pil_image = Image.open(file_path)
                parts.append(pil_image)
            except Exception as e:
                print(f"Warning: Failed to load image {record['image_filename']} for API history: {e}")

        if parts:
            formatted_history.append({
                "role": role,
                "parts": parts
            })
        
    return formatted_history

# --- Main API Functions ---

def initialize_chat_history(user_id, username, thread_id_to_load=None):
    """Initializes history and Gemini session on login/thread switch."""
    global current_threads, gemini_chat_sessions, chat_histories

    active_thread_id = thread_id_to_load
    
    if active_thread_id is None:
        active_thread_id = current_threads.get(user_id)
        
    current_threads[user_id] = active_thread_id

    if active_thread_id:
        db_history = get_history_by_user_id(user_id, thread_id=active_thread_id)
        chat_histories[user_id] = [format_db_record_for_session(record) for record in db_history]
    else:
        db_history = []
        chat_histories[user_id] = []

    if user_id in gemini_chat_sessions:
        del gemini_chat_sessions[user_id]
        
    gemini_history = format_history_for_gemini(db_history) if db_history else []
    gemini_chat_sessions[user_id] = create_chat_session(history=gemini_history)

    return active_thread_id

def get_history(user_id):
    """Returns the in-memory chat history for the current UI session."""
    return chat_histories.get(user_id, [])

def reset_chat_history(user_id):
    """Creates a new thread, resets in-memory history, and initializes a new Gemini session."""
    global current_threads, gemini_chat_sessions
    
    new_thread_id = create_new_chat_thread(user_id)
    if new_thread_id is None:
        raise Exception("Database error: Failed to create new chat thread.")

    current_threads[user_id] = new_thread_id
    chat_histories[user_id] = []
    
    if user_id in gemini_chat_sessions:
        del gemini_chat_sessions[user_id]
    
    gemini_chat_sessions[user_id] = create_chat_session()

# --- Main AI Function ---

def get_gemini_response(user_id, user_text, pil_image=None, image_filename=None):
    """
    Sends a query and an optional image to the Gemini API and returns the response.
    This is the main entry point for chat interactions.
    """
    global gemini_chat_sessions, chat_histories, current_threads
    
    # 1. Pre-checks and Initialization 
    thread_id = current_threads.get(user_id)
    if not thread_id:
        # Lazily create thread on first message
        thread_id = create_new_chat_thread(user_id)
        if not thread_id:
            return {"content": "Failed to create chat session.", "metadata": {"status": "error"}}
        current_threads[user_id] = thread_id
        # Start a fresh Gemini chat session for this user
        gemini_chat_sessions[user_id] = create_chat_session()

    chat_session = gemini_chat_sessions.get(user_id)
    response_text = "I'm sorry, my AI model is currently unavailable."
    status = "error"
    
    # 2. Analyze image if present (for both symptom and non-symptom queries)
    image_analysis_result = None
    if image_filename:
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        image_analysis_result = analyze_medical_image(image_path)
        print(f"Image analysis result: {image_analysis_result}")

    # 3. Check if query is symptom-based
    is_symptom = is_symptom_query(user_text) if user_text else False
    
    # If an image is provided, we treat it as medical even if text is minimal (e.g., "What is this?")
    if image_filename:
        is_symptom = True

    # 4. Handle non-symptom queries (only if no image and text isn't medical)
    if user_text and not is_symptom and not image_filename:
        response_text = get_non_symptom_message()
        status = "complete"
    else:
        # 5. Construct Multi-modal Content List for symptom queries
        user_parts = []

        if is_symptom:
            # Determine text input (use default if only image is provided)
            prompt_text = user_text if user_text else "Analyzing the provided medical image."
            
            # Format image analysis results only if they were successful and meet confidence threshold
            analysis_text = None
            if image_analysis_result and not image_analysis_result.get("error"):
                # Use a high confidence threshold (85%) for local models to avoid noise
                # unless the AI specifically needs to see them.
                if image_analysis_result.get("confidence", 0) >= 85.0:
                    analysis_text = format_analysis_for_prompt(image_analysis_result)
            
            # Build structured prompt using the enhanced prompt builder module
            # We tell the AI to use the analysis_text as secondary context
            structured_prompt = build_symptom_prompt(prompt_text, analysis_text)
            
            # Add a hint to Gemini to prioritize user text if image analysis seems unrelated
            if analysis_text:
                structured_prompt += "\n\nNote: If the provided Image Analysis results seem unrelated to the patient's reported symptoms, trust the symptoms more and mention the image finding as a separate possibility only if relevant."
            
            user_parts.append(structured_prompt)

        if pil_image:
            user_parts.append(pil_image)

        if not user_parts:
            return {"content": "No query or image provided.", "metadata": {"status": "mocked"}}

        # 6. Call the Gemini API for symptom queries
        api_response = send_message(chat_session, user_parts)
        response_text = api_response["content"]
        status = api_response["status"]
    
    # 6. Update DB and In-Memory History
    
    # User Message Save
    try:
        if not save_post(user_id, thread_id, user_text, image_filename, role='user'): 
            print("Warning: Failed to save user post to database.")
    except Exception as db_e:
        print(f"CRITICAL DB SAVE ERROR (User Message): {db_e}")

    # AI Message Save
    if status == "complete": 
        try:
            if not save_assistant_post(user_id, thread_id, response_text, role='assistant'):
                print("Warning: Failed to save AI post to database.")
        except Exception as db_e:
            print(f"CRITICAL DB SAVE ERROR (AI Message): {db_e}")
        
        # Save structured response if it's a symptom-based query
        if is_symptom and user_text:
            try:
                case_description, disease, probability, severity, medication, other_diagnoses, disclaimer = parse_structured_response(response_text)
                if not save_structured_response(user_id, thread_id, user_text, case_description, disease, probability, severity, medication, other_diagnoses, disclaimer):
                    print("Warning: Failed to save structured response to database.")
            except Exception as struct_e:
                print(f"Warning: Failed to parse or save structured response: {struct_e}")

    # 7. Update thread title on first user message
    try:
        if user_text and len(chat_histories.get(user_id, [])) == 0:
            title = user_text.strip()[:60]
            if title:
                update_thread_title(thread_id, user_id, title)
    except Exception as title_err:
        print(f"Thread title update warning: {title_err}")

    # 8. Update In-Memory History
    if user_id not in chat_histories:
        chat_histories[user_id] = []
        
    user_image_data_for_history = _load_image_base64_from_filename(image_filename)

    user_message_for_history = {
        "role": "user",
        "content": user_text,
        "image": user_image_data_for_history, 
        "thread_id": thread_id
    }
    chat_histories[user_id].append(user_message_for_history) 
    
    ai_message_for_history = {
        "role": "assistant",
        "content": response_text,
        "image": None, 
        "thread_id": thread_id
    }
    if status == "complete" or status == "mocked":
        chat_histories[user_id].append(ai_message_for_history)

    # 9. Return the result
    return {
        "content": response_text,
        "metadata": {"status": status}
    }





