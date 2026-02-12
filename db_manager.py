# db_manager.py

import mysql.connector
# Assuming you have a config.py file with your MySQL credentials
from config import Config 
import sys

def get_db_connection():
    "Establishes and returns a connection to the MySQL database."
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        return conn
    except mysql.connector.Error as err:
        print("="*50)
        print("❌ MySQL Connection Error!")
        print(f"1. Is your MySQL server running?")
        print(f"2. Are the credentials in config.py correct?")
        print(f"Full Error: {err}")
        print("="*50 + "\n")
        return None

def setup_database():
    """Sets up the necessary tables (Users, Chat_Threads, and Posts)."""
    conn = get_db_connection()
    if conn is None: 
        print("Connection error, database setup failed.")
        return

    cursor = conn.cursor()
    
    # 1. Users Table 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL
        )
    """)
    
    # 2. NEW: Chat_Threads Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_threads (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            title VARCHAR(255) NOT NULL DEFAULT 'New Chat',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # 3. Posts Table (MUST contain thread_id)
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                thread_id INT NOT NULL,  -- CRITICAL NEW COLUMN
                role VARCHAR(50) NOT NULL,
                text_content TEXT,
                image_filename VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (thread_id) REFERENCES chat_threads(id) ON DELETE CASCADE
            )
        """)
    except mysql.connector.Error as err:
        # Catch case where tables already exist
        if 'already exists' not in str(err):
             print(f"Post table creation warning: {err}")

    # 4. NEW: Structured Responses Table for symptom-based diagnoses
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS structured_responses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                thread_id INT NOT NULL,
                query TEXT NOT NULL,
                disease VARCHAR(255),
                probability VARCHAR(50),
                severity VARCHAR(50),
                medication TEXT,
                other_diagnoses TEXT,
                conclusion TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (thread_id) REFERENCES chat_threads(id) ON DELETE CASCADE
            )
        """)
    except mysql.connector.Error as err:
        # Catch case where tables already exist
        if 'already exists' not in str(err):
             print(f"Structured responses table creation warning: {err}")

    conn.commit()
    cursor.close()
    conn.close()
    print("Database tables created/checked successfully.")


