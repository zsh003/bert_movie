from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import List
from datetime import timedelta, datetime
from models.user import UserCreate, User, Token, UserUpdate, PasswordUpdate
from utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    get_current_admin,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from models.user import Activity
from database.database import get_database
from bson import ObjectId
import os
import shutil

router = APIRouter()

@router.post("/register", response_model=User)
async def register(user: UserCreate, request: Request = None):
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
        "is_admin": user.is_admin,
        "created_at": user_dict["created_at"]
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

@router.get("/users", response_model=list[User])
async def get_users(
    current_user: User = Depends(get_current_admin),
    request: Request = None
):
    raw_users = await request.app.mongodb["users"].find().to_list(length=None)
    users = []
    for user in raw_users:
        user["_id"] = str(user["_id"])  # 转换ObjectId为字符串
        users.append(user)
    return users

# 获取当前用户信息
@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# 更新用户个人信息
@router.put("/profile")
async def update_profile(
    user_update: UserUpdate, 
    current_user: User = Depends(get_current_user)  # 替换token参数
):
    db = get_database()
    await db.users.update_one(
        {"_id": current_user.user_id},  # 直接使用当前用户ID
        {"$set": user_update.dict(exclude_unset=True)}
    )
    return {"message": "Profile updated successfully"}

# 修改密码
@router.put("/password")
async def change_password(
    password_update: PasswordUpdate,
    current_user: User = Depends(get_current_user)  # 替换token参数
):
    db = get_database()
    # 直接使用内存中的当前用户对象验证密码
    if not verify_password(password_update.currentPassword, current_user.password):
        raise HTTPException(400, "Current password is incorrect")
    
    await db.users.update_one(
        {"_id": current_user.user_id},
        {"$set": {"password": get_password_hash(password_update.newPassword)}}
    )
    return {"message": "Password changed successfully"}

# 上传头像
@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...), 
    current_user: User = Depends(get_current_user) 
):
    db = get_database()
    
    # 创建上传目录
    upload_dir = "static/avatars"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # 生成唯一文件名
    filename = f"{current_user.user_id}{os.path.splitext(file.filename)[1]}"
    file_path = os.path.join(upload_dir, filename)
 
    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 更新用户头像URL
    avatar_url = f"/static/avatars/{filename}"
    await db.users.update_one(
        {"_id": current_user.user_id},
        {"$set": {"avatar": avatar_url}}
    )
    
    return {"url": avatar_url}

# 获取用户动态
@router.get("/activities", response_model=List[Activity])
async def get_user_activities(current_user: User = Depends(get_current_user)):
    db = get_database()
    activities = []
    
    # 获取评论
    reviews = await db.reviews.find({"user_id": str(current_user.user_id)}).to_list(None)
    for review in reviews:
        movie = await db.movies.find_one({"_id": review["movie_id"]})
        if movie:
            activities.append({
                "type": "review",
                "movie_id": str(movie["_id"]),
                "movie_title": movie["title"],
                "content": review["content"],
                "sentiment": review["sentiment"],
                "created_at": review["created_at"]
            })
    
    # 获取收藏
    favorites = await db.favorites.find({"user_id": str(current_user.user_id)}).to_list(None)
    for favorite in favorites:
        movie = await db.movies.find_one({"_id": favorite["movie_id"]})
        if movie:
            activities.append({
                "type": "favorite",
                "movie_id": str(movie["_id"]),
                "movie_title": movie["title"],
                "created_at": favorite["created_at"]
            })
    
    # 按时间排序，最新的在前面
    activities.sort(key=lambda x: x["created_at"], reverse=True)
    
    return activities 