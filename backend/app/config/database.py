import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fetch DATABASE_URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Initialize connection pool globally
db_pool = None

def init_db_pool():
    """Initialize the database connection pool."""
    global db_pool
    try:
        db_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1, 
            maxconn=10,  # Adjust max connections as needed
            dsn=DATABASE_URL
        )
        if db_pool:
            print("✅ Database Connection Pool Initialized Successfully")
    except Exception as e:
        print("❌ Error Initializing Database Pool:", str(e))

def get_db_connection():
    """Get a database connection from the pool."""
    if not db_pool:
        raise ValueError("Database connection pool is not initialized")
    
    return db_pool.getconn()

def release_db_connection(conn):
    """Release a database connection back to the pool."""
    if conn:
        db_pool.putconn(conn)

def close_db_pool():
    """Close all connections in the pool."""
    if db_pool:
        db_pool.closeall()
        print("✅ Database Connection Pool Closed Successfully")
