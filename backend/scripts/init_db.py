import json
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from datetime import datetime, timezone 
from pathlib import Path
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth import get_password_hash
from config import MONGODB_URL, DB_NAME

async def init_database():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
    # if "movies" in await db.list_collection_names():
    #     print("删除现有movies集合...")
    #     await db.drop_collection("movies")
    if "movies" not in await db.list_collection_names():
        print("创建movies集合...")
        await db.create_collection("movies")
        
        # 电影数据
        dataset_path = Path(__file__).parent.parent.parent / "dataset" / "aqy_movie_reviews.json"
        if dataset_path.exists():
            print(f"从 {dataset_path} 导入电影数据...")
            with open(dataset_path, 'r', encoding='utf-8') as f:
                movies_data = json.load(f)
            
            if movies_data:
                # 转换扩展JSON格式
                for movie in movies_data:
                    # 处理_id字段
                    if "_id" in movie and isinstance(movie["_id"], dict) and "$oid" in movie["_id"]:
                        movie["_id"] = movie["_id"]["$oid"]
                    # 处理其他可能存在的扩展JSON字段（如日期）
                    if "created_at" in movie and isinstance(movie["created_at"], dict) and "$date" in movie["created_at"]:
                        movie["created_at"] = datetime.fromisoformat(movie["created_at"]["$date"])
                    # 处理movie_id字段
                    if "movie_id" in movie:
                        # 处理$numberLong格式
                        if isinstance(movie["movie_id"], dict) and "$numberLong" in movie["movie_id"]:
                            movie["movie_id"] = int(movie["movie_id"]["$numberLong"])
                        # 处理字符串格式数字
                        elif isinstance(movie["movie_id"], str):
                            movie["movie_id"] = int(movie["movie_id"])

                await db.movies.insert_many(movies_data)
                print(f"成功导入 {len(movies_data)} 条电影数据")
                
                # 创建索引
                await db.movies.create_index([("movie_id", ASCENDING)])
                await db.movies.create_index([("title", ASCENDING)])
        else:
            print(f"警告：找不到数据文件 {dataset_path}")
    else:
        print("movies集合已存在")
    
    # 初始化用户数据
    # if "users" in await db.list_collection_names():
    #     print("删除现有users集合...")
    #     await db.drop_collection("users")
    
    if "users" not in await db.list_collection_names():
        print("创建users集合...")
        await db.create_collection("users")
    
        users = [
            {
                "user_id": "1",
                "username": "user",
                "email": "user@example.com",
                "password": get_password_hash("123456"),
                "is_admin": False,
                "created_at": datetime.now(timezone.utc),
            },
            {
                "user_id": "2",
                "username": "admin",
                "email": "admin@example.com", 
                "password": get_password_hash("123456"),
                "is_admin": True,
                "created_at": datetime.now(timezone.utc),
            }
        ]
        
        await db.users.insert_many(users)
        await db.users.create_index([("username", ASCENDING)], unique=True)
        await db.users.create_index([("email", ASCENDING)], unique=True)
    
    # 初始化评论数据
    if "reviews" in await db.list_collection_names():
        print("删除现有reviews集合...")
        await db.drop_collection("reviews")
    
    print("创建reviews集合...")
    await db.create_collection("reviews")
    
    # 导入评论数据
    reviews_path = Path(__file__).parent.parent.parent / "dataset" / "mock_reviews.json"
    if reviews_path.exists():
        print(f"从 {reviews_path} 导入评论数据...")
        with open(reviews_path, 'r', encoding='utf-8') as f:
            reviews_data = json.load(f)
        
        if reviews_data:
            await db.reviews.insert_many(reviews_data)
            print(f"成功导入 {len(reviews_data)} 条评论数据")
            
            # 创建索引
            await db.reviews.create_index([("user_id", ASCENDING)])
            await db.reviews.create_index([("movie_id", ASCENDING)])
    
    # 初始化收藏数据
    if "favorites" in await db.list_collection_names():
        print("删除现有favorites集合...")
        await db.drop_collection("favorites")
    
    print("创建favorites集合...")
    await db.create_collection("favorites")
    
    # 导入收藏数据
    favorites_path = Path(__file__).parent.parent.parent / "dataset" / "mock_favorites.json"
    if favorites_path.exists():
        print(f"从 {favorites_path} 导入收藏数据...")
        with open(favorites_path, 'r', encoding='utf-8') as f:
            favorites_data = json.load(f)
        
        if favorites_data:
            await db.favorites.insert_many(favorites_data)
            print(f"成功导入 {len(favorites_data)} 条收藏数据")
            
            # 创建索引
            await db.favorites.create_index([("user_id", ASCENDING)])
            await db.favorites.create_index([("movie_id", ASCENDING)])
    
    print("数据库初始化完成！")
    client.close()

if __name__ == "__main__":
    asyncio.run(init_database()) 