# api_handler.py
"""
Module for handling Gemini API interactions and client management.
"""

import google.generativeai as genai
from google.api_core import exceptions
from config import GEMINI_API_KEY

# --- API Key Management ---
client = None

def initialize_gemini_client():
    """
    Initializes the Gemini API client.
    
    Returns:
        bool: True if client initialized successfully, False otherwise
    """
    global client
    if GEMINI_API_KEY:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            client = genai.GenerativeModel("models/gemini-2.5-flash")
            print("Gemini client initialized successfully.")
            return True
        except Exception as e:
            print(f"Error initializing Gemini client: {e}")
            client = None
            return False
    else:
        print("Error: GEMINI_API_KEY is missing. AI response will be mocked.")
        return False

def get_gemini_client():
    """
    Returns the Gemini client instance.
    
    Returns:
        GenerativeModel or None: The Gemini client or None if not initialized
    """
    global client
    if client is None:
        initialize_gemini_client()
    return client

def create_chat_session(history=None):
    """
    Creates a new Gemini chat session.
    
    Args:
        history (list, optional): Chat history to initialize the session with
        
    Returns:
        ChatSession or str: The chat session or "MOCK_SESSION" if client unavailable
    """
    gemini_client = get_gemini_client()
    if gemini_client:
        return gemini_client.start_chat(history=history or [])
    else:
        return "MOCK_SESSION"

def send_message(chat_session, user_parts):
    """
    Sends a message to the Gemini API and returns the response.
    
    Args:
        chat_session: The Gemini chat session
        user_parts (list): List of content parts (text and/or images) to send
        
    Returns:
        dict: Dictionary with 'content' (response text) and 'status' ('complete', 'error', etc.)
    """
    if not chat_session or chat_session == "MOCK_SESSION":
        return {
            "content": "I'm sorry, my AI model is currently unavailable.",
            "status": "error"
        }
    
    try:
        response = chat_session.send_message(user_parts)
        return {
            "content": response.text,
            "status": "complete"
        }
    except exceptions.ResourceExhausted as e:
        print(f"Gemini API Resource Exhausted Error: {e}")
        return {
            "content": "I've hit my usage limit for this conversation. Please start a new chat.",
            "status": "complete"
        }
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {
            "content": "An internal API error occurred.",
            "status": "error"
        }

# Initialize client on module import
initialize_gemini_client()