import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fetch DATABASE_URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Establish and return a database connection."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in the environment variables")

    try:
        count=0
        conn = psycopg2.connect(DATABASE_URL)
        print("Connected", count+1)

        return conn
    except Exception as e:
        return None  # Handle failure gracefully
