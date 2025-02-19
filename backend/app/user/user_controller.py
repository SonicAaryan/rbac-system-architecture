from fastapi import HTTPException
from app.user.user_model import UserModel
from app.auth.auth_utils import AuthUtils
from app.auth.auth_middleware import AuthMiddleware
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

class UserController:
    @staticmethod
    async def login(login_data:LoginRequest):
        """Handles user login, verifies credentials, and generates a JWT token."""
        user = await UserModel.get_user_by_email(login_data.email)
        print("IN LOGIN API")
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
