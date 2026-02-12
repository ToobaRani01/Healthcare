
# user_db_operations.py

from db_manager import get_db_connection
import mysql.connector
from datetime import datetime

# --- User Management Functions ---
def register_user(username, email, password_hash):
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    query = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
    try:
        cursor.execute(query, (username, email, password_hash))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Registration Error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    if conn is None: return None
    cursor = conn.cursor(dictionary=True) 
    query = "SELECT * FROM users WHERE email = %s"
    try:
        cursor.execute(query, (email,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()
        
def get_user_by_id(user_id):
    conn = get_db_connection()
    if conn is None: return None
    cursor = conn.cursor(dictionary=True) 
    query = "SELECT * FROM users WHERE id = %s"
    try:
        cursor.execute(query, (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()
        
# --- Chat Thread Management ---
def create_new_chat_thread(user_id, title=None):
    """Creates a new chat thread for the user and returns the new thread_id."""
    conn = get_db_connection()
    if conn is None: return None
    cursor = conn.cursor()
    
    if title is None:
        title = f"Chat from {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    query = "INSERT INTO chat_threads (user_id, title) VALUES (%s, %s)"
    try:
        cursor.execute(query, (user_id, title))
        conn.commit()
        # Return the ID of the newly inserted row
        return cursor.lastrowid
    except mysql.connector.Error as err:
        print(f"Create Thread Error: {err}")
        return None
    finally:
        cursor.close()
        conn.close()
        
def get_user_threads(user_id):
    """Retrieves all chat threads for a given user."""
    conn = get_db_connection()
    if conn is None: return []
    cursor = conn.cursor(dictionary=True) 
    query = "SELECT id, title, created_at FROM chat_threads WHERE user_id = %s ORDER BY created_at DESC"
    try:
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_thread_by_id(user_id, thread_id):
    """Fetch a single thread ensuring ownership."""
    conn = get_db_connection()
    if conn is None: return None
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, title, created_at FROM chat_threads WHERE id = %s AND user_id = %s"
    try:
        cursor.execute(query, (thread_id, user_id))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def delete_thread(user_id, thread_id):
    """Delete a thread and its posts (cascade) if owned by the user."""
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    query = "DELETE FROM chat_threads WHERE id = %s AND user_id = %s"
    try:
        cursor.execute(query, (thread_id, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as err:
        print(f"Delete Thread Error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def update_thread_title(thread_id, user_id, new_title):
    """Set thread title if owned by user."""
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    query = "UPDATE chat_threads SET title = %s WHERE id = %s AND user_id = %s"
    try:
        cursor.execute(query, (new_title, thread_id, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as err:
        print(f"Update Thread Title Error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()


# --- Post/History Management ---
def save_post(user_id, thread_id, text_content, image_filename=None, role='user'):
    """Saves a single post (user or assistant) to the 'posts' table with the thread ID."""
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    
    query = """
        INSERT INTO posts (user_id, thread_id, role, text_content, image_filename) 
        VALUES (%s, %s, %s, %s, %s)
    """
    
    try:
        cursor.execute(query, (user_id, thread_id, role, text_content, image_filename))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Save Post Error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()
        
def save_assistant_post(user_id, thread_id, text_content, role='assistant'):
    """Saves an assistant's text response to the 'posts' table with the thread ID."""
    return save_post(user_id, thread_id, text_content, image_filename=None, role=role)

def get_history_by_user_id(user_id, thread_id):
    """Retrieves chat history for a given thread."""
    conn = get_db_connection()
    if conn is None: return []

    cursor = conn.cursor(dictionary=True) 
    
    query = """
        SELECT * FROM posts 
        WHERE user_id = %s AND thread_id = %s 
        ORDER BY created_at ASC
    """
    params = [user_id, thread_id]
        
    history_records = []
    try:
        cursor.execute(query, params)
        history_records = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Get History Error: {err}")
    finally:
        cursor.close()
        conn.close()
        
    return history_records

# --- Structured Response Management ---
def save_structured_response(user_id, thread_id, query, disease=None, probability=None, severity=None, medication=None, other_diagnoses=None, conclusion=None):
    """Saves a structured response to the 'structured_responses' table."""
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    
    query_sql = """
        INSERT INTO structured_responses (user_id, thread_id, query, disease, probability, severity, medication, other_diagnoses, conclusion) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    try:
        cursor.execute(query_sql, (user_id, thread_id, query, disease, probability, severity, medication, other_diagnoses, conclusion))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Save Structured Response Error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()