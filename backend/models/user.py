from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None

class PasswordUpdate(BaseModel):
    currentPassword: str
    newPassword: str
    confirmPassword: str

class User(UserBase):
    _id: str
    avatar: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class Activity(BaseModel):
    type: Literal["review", "favorite"]  # 活动类型：评论或收藏
    movie_id: str
    movie_title: str
    content: Optional[str] = None  # 评论内容，仅在type为review时有值
    sentiment: Optional[str] = None  # 情感分析结果，仅在type为review时有值
    created_at: datetime

    class Config:
        from_attributes = True 