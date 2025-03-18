from fastapi import HTTPException
import psycopg2
from app.config.database import get_db_connection, release_db_connection

class UserModel:
    @staticmethod
    async def get_user_by_email(email):
        """Fetch a user by email from the database and return as a dictionary."""
        query = "SELECT id, first_name, last_name, email, password, mobile, address, role, token, created_at, updated_at FROM users WHERE email = %s"
        
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (email,))
            row = cursor.fetchone()

            if row:
                user = {
                    "id": row[0],
                    "first_name": row[1],
                    "last_name": row[2],
                    "email": row[3],
                    "password": row[4],
                    "mobile": row[5],
                    "address": row[6],
                    "role": row[7],
                    "token": row[8],
                    "created_at": row[9],
                    "updated_at": row[10]
                }
                return user
            return None

        finally:
            cursor.close()
            release_db_connection(conn)  # ✅ Release connection back to the pool

    @staticmethod
    async def update_user_token(user_id, token):
        """Update user token after successful login."""
        query = "UPDATE users SET token = %s, updated_at = NOW() WHERE id = %s"
        
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (token, user_id))
            conn.commit()
        finally:
            cursor.close()
            release_db_connection(conn)  # ✅ Release connection back to the pool
            
    @staticmethod
    async def get_all_users_with_permissions():
    # """Fetch all users with their role permissions using a JOIN query."""
        query = """SELECT u.id, u.email, u.first_name, u.last_name, u.role, rp.permission_name, rp.is_allowed FROM users u LEFT JOIN role_permissions rp ON u.role = rp.role_name ORDER BY u.id, rp.permission_name"""
    
        conn = get_db_connection()
        cursor = conn.cursor()
    
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            users = {}
        
            for row in rows:
                user_id = row[0]
                if user_id not in users:
                    users[user_id] = {
                        "id": row[0],
                        "email": row[1],
                        "first_name": row[2],
                        "last_name": row[3],
                        "role": row[4],
                        "permissions": {}
                    }
                if row[5]:  # permission_name
                    users[user_id]["permissions"][row[5]] = row[6]  # is_allowed
        
            return list(users.values())
        except psycopg2.Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            cursor.close()
            release_db_connection(conn)
            
    @staticmethod
    async def get_all_users_with_permissions():
        """Fetch all users with their role permissions using a JOIN query."""
        query = """
        SELECT u.id, u.email, u.first_name, u.last_name, u.role, rp.permission_name, rp.is_allowed
        FROM users u
        LEFT JOIN role_permissions rp ON u.role = rp.role_name
        ORDER BY u.id, rp.permission_name
        """
    
        conn = get_db_connection()
        cursor = conn.cursor()
    
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            users = {}
        
            for row in rows:
                user_id = row[0]
                if user_id not in users:
                    users[user_id] = {
                        "id": row[0],
                        "email": row[1],
                        "first_name": row[2],
                        "last_name": row[3],
                        "role": row[4],
                        "permissions": {}
                    }
                if row[5]:  # permission_name
                    users[user_id]["permissions"][row[5]] = row[6]  # is_allowed
        
            return list(users.values())
        except psycopg2.Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            cursor.close()
        release_db_connection(conn)
