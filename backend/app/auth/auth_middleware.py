import jwt
import datetime
import os
import bcrypt
import psycopg2
from app.config.database import get_db_connection

class AuthMiddleware:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")  # Fallback if env variable is missing

    @staticmethod
    async def signup(first_name, last_name, email, password, mobile, address, role):
        """Registers a new user in the database."""
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        query = """
        INSERT INTO users (first_name, last_name, email, password, mobile, address, role, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW()) RETURNING id
        """

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query, (first_name, last_name, email, hashed_password, mobile, address, role))
            user_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            return {"message": "User created successfully", "user_id": user_id}
        except psycopg2.Error as e:
            return {"error": str(e)}

    @staticmethod
    def login(username, password):
        """Handles user login and generates a JWT token."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, password, role FROM users WHERE email = %s", (username,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode(), user[1].encode()):
            token = jwt.encode(
                {
                    "user_id": user[0],
                    "role": user[2],
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                },
                AuthMiddleware.SECRET_KEY,
                algorithm="HS256"
            )

            cursor.execute(
                "INSERT INTO sessions (user_id, token, expires_at) VALUES (%s, %s, %s)",
                (user[0], token, datetime.datetime.utcnow() + datetime.timedelta(hours=1))
            )
            conn.commit()
            cursor.close()
            conn.close()

            return {"token": token}

        cursor.close()
        conn.close()
        return {"error": "Invalid credentials"}

    @staticmethod
    def logout(token):
        """Handles user logout by deleting the session token."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM sessions WHERE token = %s", (token,))
        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Logged out successfully"}
