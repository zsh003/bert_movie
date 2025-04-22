from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from models.user import User
from utils.auth import get_current_user
from database.database import get_database
import uuid

router = APIRouter()

@router.post("/{movie_id}", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    movie_id: int,
    current_user: User = Depends(get_current_user)
):
    db = get_database()
    
    # 检查是否已经收藏
    existing = await db.favorites.find_one({
        "user_id": str(current_user.user_id),
        "movie_id": movie_id
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="已经收藏过这部电影")
    
    favorite = {
        "_id": str(uuid.uuid4()),
        "user_id": str(current_user.user_id),
        "movie_id": movie_id,
        "created_at": datetime.utcnow()
    }
    
    await db.favorites.insert_one(favorite)
    return favorite

@router.get("/", response_model=List[dict])
async def get_my_favorites(current_user: User = Depends(get_current_user)):
    db = get_database()
    # 获取用户的收藏电影列表
    favorites = await db.favorites.find({"user_id": str(current_user.user_id)}).sort("created_at", -1).to_list(None)
    # 获取收藏电影的详细信息
    movie_ids = [fav["movie_id"] for fav in favorites]
    movies = await db.movies.find({"movie_id": {"$in": movie_ids}}).to_list(None)
    # 将收藏时间添加到电影信息中
    movie_dict = {movie["movie_id"]: movie for movie in movies}
    result = []
    for fav in favorites:
        if fav["movie_id"] in movie_dict:
            movie_info = movie_dict[fav["movie_id"]].copy()
            movie_info.update({
                "favorite_id": str(fav["_id"]),  # 转换 ObjectId 为字符串
                "favorited_at": fav["created_at"],
                "_id": str(movie_info["_id"])    # 转换电影文档的 ObjectId
            })
            result.append(movie_info)
    
    return result

@router.delete("/{favorite_id}")
async def remove_favorite(
    favorite_id: str,
    current_user: User = Depends(get_current_user)
):
    db = get_database()
    favorite = await db.favorites.find_one({"_id": favorite_id})
    
    if not favorite:
        raise HTTPException(status_code=404, detail="收藏记录不存在")
    
    if favorite["user_id"] != str(current_user.user_id):
        raise HTTPException(status_code=403, detail="没有权限删除此收藏")
    
    await db.favorites.delete_one({"_id": favorite_id})
    return {"message": "已取消收藏"}

@router.get("/check/{movie_id}")
async def check_favorite(
    movie_id: int,
    current_user: User = Depends(get_current_user)
):
    db = get_database()
    favorite = await db.favorites.find_one({
        "user_id": str(current_user.user_id),
        "movie_id": movie_id
    })
    return {"is_favorite": bool(favorite)} 