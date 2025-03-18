from app.config.database import get_db_connection,release_db_connection

class AuthService:    
    @staticmethod
    def logout(token: str):
        """Handles user logout by deleting the session token from the database."""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            print("Received token for logout:", token)  # Debugging
            cursor.execute("UPDATE users SET token = NULL WHERE token = %s", (token,))

            if cursor.rowcount == 0:
                print("❌ Token not found in database")  # Debugging
                return {"error": "Invalid token or already logged out"}

            conn.commit()
            print("✅ Token deleted successfully")  # Debugging
            return {"message": "Logged out successfully"}

        except Exception as e:
            print("❌ Database error:", str(e))  # Debugging
            return {"error": str(e)}
        finally:
            if cursor:
                cursor.close()
            if conn:
                release_db_connection(conn)