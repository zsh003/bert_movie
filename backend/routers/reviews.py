from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from models.user import User
from utils.auth import get_current_user
from database.database import get_database
import uuid

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_review(
    movie_id: int,
    content: str,
    sentiment: str,
    current_user: User = Depends(get_current_user)
):
    db = get_database()
    review = {
        "_id": str(uuid.uuid4()),
        "user_id": str(current_user.user_id),
        "movie_id": movie_id,
        "content": content,
        "sentiment": sentiment,
        "created_at": datetime.utcnow(),
        "username": current_user.username  # 添加用户名方便前端显示
    }
    
    await db.reviews.insert_one(review)
    return review

@router.get("/movie/{movie_id}", response_model=List[dict])
async def get_movie_reviews(movie_id: int):
    db = get_database()
    reviews = await db.reviews.find({"movie_id": movie_id}).sort("created_at", -1).to_list(None)
    return reviews

@router.get("/user/me", response_model=List[dict])
async def get_my_reviews(current_user: User = Depends(get_current_user)):
    db = get_database()
    reviews = await db.reviews.find({"user_id": str(current_user.user_id)}).sort("created_at", -1).to_list(None)
    return reviews

@router.delete("/{review_id}")
async def delete_review(
    review_id: str,
    current_user: User = Depends(get_current_user)
):
    db = get_database()
    review = await db.reviews.find_one({"_id": review_id})
    
    if not review:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    if review["user_id"] != str(current_user.user_id):
        raise HTTPException(status_code=403, detail="没有权限删除此评论")
    
    await db.reviews.delete_one({"_id": review_id})
    return {"message": "评论已删除"} 