from fastapi import APIRouter, Request
from typing import List
import jieba
from collections import Counter
import config

router = APIRouter()

@router.get("/sentiment/{movie_id}")
async def get_movie_sentiment(movie_id: int, request: Request):
    movie = await request.app.mongodb[config.COLLECTION_NAME].find_one({"movie_id": movie_id})
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
    movie = await request.app.mongodb[config.COLLECTION_NAME].find_one({"movie_id": movie_id})
    if not movie:
        return {"error": "Movie not found"}
    
    reviews = movie.get("reviews", [])
    words = []
    for review in reviews:
        words.extend(jieba.cut(review["content"]))
    
    word_count = Counter(words)
    return [{"word": word, "count": count} for word, count in word_count.most_common(50)]

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
    
    user_activity = await request.app.mongodb[config.COLLECTION_NAME].aggregate(pipeline).to_list(length=None)
    return user_activity 