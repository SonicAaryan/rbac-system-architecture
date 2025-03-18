from fastapi import APIRouter, Depends
from app.user.user_controller import UserController,SignupRequest ,LoginRequest
from app.user.user_middleware import get_current_user
from app.user.user_middleware import get_current_user 
# from app.auth.auth_middleware import require_user

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

# @router.get("/users/permissions", dependencies=[Depends(require_user)])  # Only authenticated users can access
# async def get_users_with_permissions():
#     return await user_model.get_all_users_with_permissions()

@router.get("/reports/{user_id}")  # Only authenticated users can access (adjust to require_admin if needed)
async def get_reports_by_user_id(user_id: int):
    return await UserController.get_reports_by_user_id(user_id)