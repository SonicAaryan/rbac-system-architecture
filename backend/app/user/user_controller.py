from fastapi import Depends, HTTPException
import psycopg2
from app.user.user_model import CreateReportRequest, UserModel
from app.auth.auth_utils import AuthUtils
from app.auth.auth_service import AuthService
from app.auth.auth_middleware import AuthMiddleware
from app.user.user_middleware import get_current_user
from app.user.user_model import UpdateUserRequest
from app.config.database import get_db_connection, release_db_connection
from pydantic import BaseModel, EmailStr

class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    mobile: str
    address: str
    role: str="user"  # Should be either 'admin' or 'user'

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LogoutRequest(BaseModel):
    token:str
    

class UserController:
    
    # """Handles user login, verifies credentials, and generates a JWT token."""
    @staticmethod
    async def login(login_data:LoginRequest):
        user = await UserModel.get_user_by_email(login_data.email)
        # print("IN LOGIN API")
        if not user or not AuthUtils.verify_password(login_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = AuthUtils.generate_token(user["id"])
        await UserModel.update_user_token(user["id"], token)  # Ensure token is stored in the DB

        return {"message": "Login successful", "data": user}

    
    # """Handles user signup and inserts new user into the database."""
    @staticmethod
    async def signup(signup_data):
        existing_user = await UserModel.get_user_by_email(signup_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        response = await AuthMiddleware.signup(
            signup_data.first_name,
            signup_data.last_name,
            signup_data.email,
            signup_data.password,
            signup_data.mobile,
            signup_data.address,
            signup_data.role
        )

        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])

        return response
    
    
    # """Handles user logout by deleting the session token from the database."""
    @staticmethod
    async def logout(current_user: dict):

        # ✅ Debugging Step: Print received token
        print("Received logout request with user:", current_user)

        # ✅ Ensure token is passed correctly
        if not current_user or "id" not in current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")

        user_id = current_user["id"]
        token = current_user.get("token","") #Get token from the current user 

        response = AuthService.logout(token)

        if "error" in response:
            raise HTTPException(status_code=400, detail=response["error"])

        return {"message": "Logged out successfully"}
    
    
    # """Fetch reports for a specific user using a LEFT JOIN raw query."""
    @staticmethod
    async def get_reports_by_user_id(user_id: int):
        query = """
        SELECT u.first_name, u.last_name, u.role,u.address, r.report_title, r.status, r.submission_date
        FROM users u
        LEFT JOIN reports r ON u.id = r.user_id
        WHERE u.id = %s
        ORDER BY r.submission_date DESC
        """
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            
            if not rows:
                raise HTTPException(status_code=404, detail="User or reports not found")
            
            # Get user details from the first row (assuming user_id is unique)
            if rows:
                user = {
                    "first_name": rows[0][0],
                    "last_name": rows[0][1],
                    "role": rows[0][2],
                    "address":rows[0][3],
                    "reports":[],
                }
                
                # Collect all reports into the reports list
                for row in rows:
                    if row[4]:  # Check if report_title exists (not None from LEFT JOIN)
                        report = {
                            "report_title": row[4],
                            "status": row[5],
                            "submission_date": row[6].isoformat() if row[6] else None
                        }
                        user["reports"].append(report)
                
                return user
            
        except psycopg2.Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            cursor.close()
            release_db_connection(conn)

    
    # """Fetch all users (admin-only)."""
    @staticmethod
    async def get_all_users(current_user: dict = Depends(get_current_user)):
        print(current_user)
        if current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Only admins can access this endpoint")

        query = """SELECT id, first_name, last_name, email, mobile, address, role, created_at FROM users ORDER BY id"""
    
        conn = get_db_connection()
        cursor = conn.cursor()
    
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            users = [
                {
                    "id": row[0],
                    "first_name": row[1],
                    "last_name": row[2],
                    "email": row[3],
                    "mobile": row[4],
                    "address": row[5],
                    "role": row[6],
                    "created_at": row[7].isoformat() if row[7] else None
                }
                for row in rows
            ]
            return users
        except psycopg2.Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            cursor.close()
            release_db_connection(conn)
    
    #"""Update User Details (self or admin)"""
    @staticmethod
    async def update_user(user_id: int, update_data: UpdateUserRequest, current_user: dict = Depends(get_current_user)):
        if current_user["id"] != user_id and current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="You can only update your own details or must be an admin")
    
        print("In Update_User")
        updates = []
        params = []
        if update_data.first_name:
            updates.append("first_name = %s")
            params.append(update_data.first_name)
        if update_data.last_name:
            updates.append("last_name = %s")
            params.append(update_data.last_name)
        if update_data.mobile:
            updates.append("mobile = %s")
            params.append(update_data.mobile)
        if update_data.address:
            updates.append("address = %s")
            params.append(update_data.address)
    
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
    
        updates.append("updated_at = NOW()")
        params.append(user_id)
    
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"

        conn = get_db_connection()
        cursor = conn.cursor()
    
        try:
            cursor.execute(query, params)
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")
            conn.commit()
            return {"message": "User updated successfully"}
        except psycopg2.Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            cursor.close()
            release_db_connection(conn)
    
    
    # """Delete a User(Admin-only)"""
    @staticmethod
    async def delete_user(user_id:int, current_user: dict = Depends(get_current_user)):
        if current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Only admins can delete users")
        
        query="delete from users where id = %s"
        
        conn=get_db_connection()
        cursor=conn.cursor()
        
        try:
            cursor.execute(query,(user_id,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="User Not Found!")
            conn.commit()
            return {"message":"User deleted successfully"}
        except psycopg2.Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            cursor.close()
            release_db_connection(conn)
            
    # """Create a new report for the authenticated user."""
    @staticmethod
    async def create_report(report_data: CreateReportRequest, current_user: dict = Depends(get_current_user)):
        query="""insert into reports (user_id,report_title, report_content, status, submission_date, created_at, updated_at) values (%s, %s, %s, %s, NOW(), NOW(), NOW()) returning id"""
        
        conn=get_db_connection
        cursor=conn.cursor()

        try:
            cursor.execute(query, (current_user["id"], report_data.report_title,report_data.report_content, report_data.status))
            report_id= cursor.fetchone()[0]
            conn.commit()
            return {"message":"Report created successfully","report_id":report_id}
        except psycopg2.Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            cursor.close()
            release_db_connection(conn)