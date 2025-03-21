from fastapi import HTTPException
import psycopg2
from app.user.user_model import UserModel
from app.auth.auth_utils import AuthUtils
from app.auth.auth_service import AuthService
from app.auth.auth_middleware import AuthMiddleware
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
    @staticmethod
    async def login(login_data:LoginRequest):
        """Handles user login, verifies credentials, and generates a JWT token."""
        user = await UserModel.get_user_by_email(login_data.email)
        # print("IN LOGIN API")
        if not user or not AuthUtils.verify_password(login_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = AuthUtils.generate_token(user["id"])
        await UserModel.update_user_token(user["id"], token)  # Ensure token is stored in the DB

        return {"message": "Login successful", "data": user}

    @staticmethod
    async def signup(signup_data):
        """Handles user signup and inserts new user into the database."""
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
    
    @staticmethod
    async def logout(current_user: dict):
        """Handles user logout by deleting the session token from the database."""

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
    
    @staticmethod
    async def get_reports_by_user_id(user_id: int):
        """Fetch reports for a specific user using a LEFT JOIN raw query."""
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
            
            # return reports
        except psycopg2.Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            cursor.close()
            release_db_connection(conn)
    
    
