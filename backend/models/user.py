from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class UserBase(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    is_admin: bool = False
    created_at: datetime

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None

class PasswordUpdate(BaseModel):
    currentPassword: str
    newPassword: str
    confirmPassword: str

class User(UserBase):
    id: str = Field(..., alias="_id") # 定义别名
    avatar: Optional[str] = None
    
    class Config:
        populate_by_name = True  # 允许通过别名进行赋值
        json_encoders = {
            object: lambda v: str(v)  # 将ObjectId转换为字符串
        }
        from_attributes = True

class Activity(BaseModel):
    type: Literal["review", "favorite"]  # 活动类型：评论或收藏
    movie_id: int
    movie_title: str
    content: Optional[str] = None  # 评论内容，仅在type为review时有值
    sentiment: Optional[str] = None  # 情感分析结果，仅在type为review时有值
    created_at: datetime

    class Config:
        from_attributes = True 