from fastapi import APIRouter, Depends
from app.user.user_controller import UserController,SignupRequest ,LoginRequest
from app.user.user_middleware import get_current_user
from app.user.user_middleware import get_current_user 

router = APIRouter()

@router.post("/login")
async def login(login_data:LoginRequest):
    return await UserController.login(login_data)


@router.post("/signup")
async def signup(signup_data: SignupRequest):
    return await UserController.signup(signup_data)

@router.post("/logout", dependencies=[Depends(get_current_user)])
async def logout(current_user: dict = Depends(get_current_user)):
    return await UserController.logout(current_user)

@router.get("/users", dependencies=[Depends(get_current_user)])  # Only admins can access
async def get_all_users(current_user: dict = Depends(get_current_user)):
    return await UserController.get_all_users(current_user)

@router.get("/reports/{user_id}")  # Only authenticated users can access (adjust to require_admin if needed)
async def get_reports_by_user_id(user_id: int):
    return await UserController.get_reports_by_user_id(user_id)