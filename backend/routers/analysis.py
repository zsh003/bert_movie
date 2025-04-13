from fastapi import APIRouter, Request, Depends
from typing import List
import jieba
from collections import Counter
from datetime import datetime, timedelta
from utils.auth import get_current_user
from models.user import User
import random
from jieba import analyse

router = APIRouter()

@router.get("/sentiment/{movie_id}")
async def get_movie_sentiment(movie_id: int, request: Request):
    movie = await request.app.mongodb["movies"].find_one({"movie_id": movie_id})
    if not movie:
        return {"error": "Movie not found"}
    
    reviews = movie.get("reviews", [])
    # 这里可以接入情感分析模型
    # 示例返回格式
    return {
        "positive": len([r for r in reviews if len(r["content"]) > 20]),
        "neutral": len([r for r in reviews if 10 <= len(r["content"]) <= 20]),
        "negative": len([r for r in reviews if len(r["content"]) < 10])
    }

@router.get("/word-cloud/{movie_id}")
async def get_word_cloud(movie_id: int, request: Request):
    movie = await request.app.mongodb["movies"].find_one({"movie_id": movie_id})
    if not movie:
        return {"error": "Movie not found"}
    
    reviews = movie.get("reviews", [])
    words = []
    for review in reviews:
        words.extend(jieba.cut(review["content"]))
    
    word_count = Counter(words)
    return [{"word": word, "count": count} for word, count in word_count.most_common(50)]

@router.get("/sentiment-trend")
async def get_sentiment_trend(request: Request):
    # 获取最近7天的情感分析趋势
    dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    dates.reverse()
    
    # 示例数据
    return {
        "dates": dates,
        "positive": [random.randint(50, 100) for _ in range(7)],
        "neutral": [random.randint(30, 70) for _ in range(7)],
        "negative": [random.randint(10, 40) for _ in range(7)]
    }

@router.get("/user-activity-trend")
async def get_user_activity_trend(request: Request):
    # 获取最近7天的用户活跃度
    dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    dates.reverse()
    
    pipeline = [
        {
            "$unwind": "$reviews"
        },
        {
            "$group": {
                "_id": "$reviews.uname",
                "review_count": {"$sum": 1}
            }
        },
        {
            "$sort": {"review_count": -1}
        }
    ]
    
    user_activity = await request.app.mongodb["movies"].aggregate(pipeline).to_list(length=None)
    counts = [activity["review_count"] for activity in user_activity[:7]]
    
    return {
        "dates": dates,
        "counts": counts
    }

@router.get("/comment-length-distribution")
async def get_comment_length_distribution(request: Request):
    pipeline = [
        {
            "$unwind": "$reviews"
        },
        {
            "$project": {
                "content_length": {"$strLenCP": "$reviews.content"}
            }
        }
    ]
    
    comments = await request.app.mongodb["movies"].aggregate(pipeline).to_list(length=None)
    
    short = len([c for c in comments if c["content_length"] < 50])
    medium = len([c for c in comments if 50 <= c["content_length"] <= 200])
    long = len([c for c in comments if c["content_length"] > 200])
    
    return {
        "short": short,
        "medium": medium,
        "long": long
    }

@router.get("/movie-rating-distribution")
async def get_movie_rating_distribution(request: Request):
    # 示例数据 - 实际应用中需要从数据库获取
    return {
        "ratings": [
            random.randint(10, 50),  # 1分
            random.randint(20, 60),  # 2分
            random.randint(40, 80),  # 3分
            random.randint(60, 100), # 4分
            random.randint(80, 120)  # 5分
        ]
    }

@router.get("/user-activity")
async def get_user_activity(request: Request):
    pipeline = [
        {"$unwind": "$reviews"},
        {"$group": {
            "_id": "$reviews.uname",
            "review_count": {"$sum": 1},
            "movies": {"$addToSet": "$title"}
        }},
        {"$sort": {"review_count": -1}},
        {"$limit": 10}
    ]
    
    user_activity = await request.app.mongodb["movies"].aggregate(pipeline).to_list(length=None)
    return user_activity
