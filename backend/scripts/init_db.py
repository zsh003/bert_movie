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
    
    if "aqy_movie_reviews" not in await db.list_collection_names():
        print("创建movies集合...")
        await db.create_collection("aqy_movie_reviews")
        
        # 电影数据
        dataset_path = Path(__file__).parent.parent.parent / "dataset" / "aqy_movie_reviews.json"
        if dataset_path.exists():
            print(f"从 {dataset_path} 导入电影数据...")
            with open(dataset_path, 'r', encoding='utf-8') as f:
                movies_data = json.load(f)
            
            if movies_data:
                await db.movies.insert_many(movies_data)
                print(f"成功导入 {len(movies_data)} 条电影数据")
                
                # 创建索引
                await db.movies.create_index([("movie_id", ASCENDING)])
                await db.movies.create_index([("title", ASCENDING)])
        else:
            print(f"警告：找不到数据文件 {dataset_path}")
    else:
        print("电影集合已存在")
    
    # 用户集合
    if "users" in await db.list_collection_names():
        print("删除现有users集合...")
        await db.drop_collection("users")
    if "users" not in await db.list_collection_names():
        print("创建users集合...")
        await db.create_collection("users")
        
        users = [
            {
                "username": "user",
                "email": "user@example.com",
                "password": get_password_hash("123456"),
                "is_admin": False,
                "created_at": datetime.now(timezone.utc),  # UTC时区时间
            },
            {
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
    
    else:
        print("用户集合已存在")
    print("数据库初始化完成！")
    client.close()

if __name__ == "__main__":
    asyncio.run(init_database()) 