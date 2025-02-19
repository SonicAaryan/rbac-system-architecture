from fastapi import APIRouter, Depends
from app.user.user_controller import UserController,SignupRequest ,LoginRequest
# from app.user.user_middleware import get_current_user

router = APIRouter()

@router.post("/login")
async def login(login_data:LoginRequest):
    return await UserController.login(login_data)


@router.post("/signup")
async def signup(signup_data: SignupRequest):
    return await UserController.signup(signup_data)

