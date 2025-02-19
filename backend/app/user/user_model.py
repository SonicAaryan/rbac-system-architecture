from app.config.database import get_db_connection

class UserModel:
    @staticmethod
    async def get_user_by_email(email):
        """Fetch a user by email from the database and return as a dictionary."""
        query = "SELECT id, first_name, last_name, email, password, mobile, address, role, token, created_at, updated_at FROM users WHERE email = %s"
        conn = get_db_connection()  # Get DB connection
        cursor = conn.cursor()

        try:
            cursor.execute(query, (email,))
            row = cursor.fetchone()  # Fetch single user record
            
            if row:
                # ✅ Convert tuple to dictionary for easy access
                user = {
                    "id": row[0],
                    "first_name": row[1],
                    "last_name": row[2],
                    "email": row[3],
                    "password": row[4],  # Fix: Ensure this is the correct field for password
                    "mobile": row[5],
                    "address": row[6],
                    "role": row[7],
                    "token": row[8],
                    "created_at": row[9],
                    "updated_at": row[10]
                }
                return user
            else:
                return None  # No user found

        finally:
            cursor.close()
            conn.close()  # Ensure DB connection is closed

    @staticmethod
    async def update_user_token(user_id, token):
        """Update user token after successful login."""
        query = "UPDATE users SET token = %s, updated_at = NOW() WHERE id = %s"
        conn = get_db_connection()  # Get DB connection
        cursor = conn.cursor()

        try:
            cursor.execute(query, (token, user_id))
            conn.commit()  # Commit changes
        finally:
            cursor.close()
            conn.close()  # Close DB connection
