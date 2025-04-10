from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from models.user import UserCreate, User, Token
from utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    get_current_admin,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from bson import ObjectId

router = APIRouter()

@router.post("/register", response_model=User)
async def register(user: UserCreate, request: Request):
    # 检查用户名是否已存在
    if await request.app.mongodb["users"].find_one({"username": user.username}):
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # 创建新用户
    user_dict = user.dict()
    user_dict["password"] = get_password_hash(user.password)
    user_dict["_id"] = str(ObjectId())
    
    await request.app.mongodb["users"].insert_one(user_dict)
    
    return {
        "id": user_dict["_id"],
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin
    }

@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None
):
    user = await request.app.mongodb["users"].find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/users", response_model=list[User])
async def get_users(
    current_user: User = Depends(get_current_admin),
    request: Request = None
):
    users = await request.app.mongodb["users"].find().to_list(length=None)
    return users 