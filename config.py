
import os


# API keys
#  GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCtQ7kO58F0eReP3SFILO0JA4mN0joC2SU")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDs5lr3t5Kd9n6xAdnBWbZ9MVgy2wd0ALs")



class Config:
    """Database configuration settings."""

    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "TR@GCUH#2024!AI")
    MYSQL_DB = os.getenv("MYSQL_DB", "chatbot")