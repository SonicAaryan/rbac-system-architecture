import bcrypt
import jwt
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timedelta
from app.config.database import get_db_connection  # Ensure database connection is imported

# Load environment variables
load_dotenv()

# Default SECRET_KEY if not found in .env
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

class AuthUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes the password securely using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies the hashed password."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def generate_token(user_id: int) -> str:
        """Generates a JWT token with a 2-hour expiry."""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=2)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")  # ✅ Fixed return type
