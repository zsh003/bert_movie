from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import Counter
import jieba.analyse as analyse
from database.database import get_database
from utils.auth import get_current_user
from models.user import User

router = APIRouter()

@router.get("/reviews")
async def get_review_analytics(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """获取影评数据分析"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    today = datetime.now()
    thirty_days_ago = today - timedelta(days=30)
    
    # 1. 情感分布统计
    pipeline = [
        {"$unwind": "$reviews"},
        {
            "$group": {
                "_id": "$reviews.sentiment",
                "count": {"$sum": 1}
            }
        }
    ]
    
    sentiment_results = await request.app.mongodb["movies"].aggregate(pipeline).to_list(length=None)
    sentiment_distribution = {
        "positive": 0,
        "neutral": 0,
        "negative": 0
    }
    for result in sentiment_results:
        if result["_id"] in sentiment_distribution:
            sentiment_distribution[result["_id"]] = result["count"]
    
    # 2. 评论数量趋势（最近30天）
    pipeline = [
        {"$unwind": "$reviews"},
        {
            "$match": {
                "reviews.created_at": {
                    "$gte": thirty_days_ago
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$reviews.created_at"
                    }
                },
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    trend_results = await request.app.mongodb["movies"].aggregate(pipeline).to_list(length=None)
    
    # 填充缺失的日期
    date_counts = {result["_id"]: result["count"] for result in trend_results}
    dates = []
    counts = []
    
    for i in range(30):
        date = thirty_days_ago + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        dates.append(date_str)
        counts.append(date_counts.get(date_str, 0))
    
    review_trend = {
        "dates": dates,
        "counts": counts
    }
    
    # 3. 热门关键词提取（分批处理）
    pipeline = [
        {"$unwind": "$reviews"},
        {"$match": {
            "reviews.created_at": {
                "$gte": thirty_days_ago
            }
        }},
        {"$project": {
            "content": "$reviews.content"
        }},
        {"$limit": 1000}  # 限制处理最近1000条评论
    ]
    
    content_results = await request.app.mongodb["movies"].aggregate(pipeline).to_list(length=None)
    if content_results:
        all_content = " ".join(doc["content"] for doc in content_results)
        keywords = analyse.extract_tags(all_content, topK=50, withWeight=True)
        keywords_data = [
            {"word": word, "weight": round(weight * 100, 2)}
            for word, weight in keywords
        ]
    else:
        keywords_data = []
    
    return {
        "sentimentDistribution": sentiment_distribution,
        "reviewTrend": review_trend,
        "keywords": keywords_data
    }

@router.get("/movies")
async def get_movie_analytics(request: Request, current_user: User = Depends(get_current_user)):
    """获取电影数据分析"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    # 1. 评分分布
    pipeline = [
        {
            "$group": {
                "_id": "$rating",
                "count": {"$sum": 1}
            }
        }
    ]
    
    rating_results = await request.app.mongodb["movies"].aggregate(pipeline).to_list(length=None)
    rating_data = {
        "ratings": list(range(1, 6)),
        "counts": [0] * 5
    }
    for result in rating_results:
        if result["_id"] and 1 <= result["_id"] <= 5:
            rating_data["counts"][int(result["_id"]) - 1] = result["count"]

    # 2. 类型分布
    pipeline = [
        {"$unwind": "$genre"},
        {
            "$group": {
                "_id": "$genre",
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    
    genre_results = await request.app.mongodb["movies"].aggregate(pipeline).to_list(length=None)
    genre_data = {
        "genres": [result["_id"] for result in genre_results],
        "counts": [result["count"] for result in genre_results]
    }

    # 3. 发布趋势（最近12个月）
    twelve_months_ago = datetime.now() - timedelta(days=365)
    pipeline = [
        {
            "$match": {
                "release_date": {
                    "$gte": twelve_months_ago
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m",
                        "date": "$release_date"
                    }
                },
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    trend_results = await request.app.mongodb["movies"].aggregate(pipeline).to_list(length=None)
    
    # 填充缺失的月份
    months_data = {result["_id"]: result["count"] for result in trend_results}
    months = []
    counts = []
    
    current_date = twelve_months_ago
    while current_date <= datetime.now():
        month_key = current_date.strftime("%Y-%m")
        months.append(month_key)
        counts.append(months_data.get(month_key, 0))
        current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
    
    release_trend = {
        "months": months,
        "counts": counts
    }

    return {
        "ratingDistribution": rating_data,
        "genreDistribution": genre_data,
        "releaseTrend": release_trend
    }

@router.get("/users")
async def get_user_analytics(request: Request, current_user: User = Depends(get_current_user)):
    """获取用户数据分析"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    # 1. 用户活跃度（最近30天）
    today = datetime.now()
    thirty_days_ago = today - timedelta(days=30)
    
    pipeline = [
        {"$unwind": "$reviews"},
        {
            "$match": {
                "reviews.created_at": {
                    "$gte": thirty_days_ago
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "date": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$reviews.created_at"
                        }
                    },
                    "user": "$reviews.uname"
                }
            }
        },
        {
            "$group": {
                "_id": "$_id.date",
                "active_users": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    activity_results = await request.app.mongodb["movies"].aggregate(pipeline).to_list(length=None)
    
    # 填充缺失的日期
    date_counts = {result["_id"]: result["active_users"] for result in activity_results}
    dates = []
    counts = []
    
    for i in range(30):
        date = thirty_days_ago + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        dates.append(date_str)
        counts.append(date_counts.get(date_str, 0))
    
    activity_data = {
        "dates": dates,
        "counts": counts
    }

    # 2. 用户注册趋势（最近12个月）
    twelve_months_ago = today - timedelta(days=365)
    pipeline = [
        {
            "$match": {
                "created_at": {
                    "$gte": twelve_months_ago
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m",
                        "date": "$created_at"
                    }
                },
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    registration_results = await request.app.mongodb["users"].aggregate(pipeline).to_list(length=None)
    
    # 填充缺失的月份
    months_data = {result["_id"]: result["count"] for result in registration_results}
    months = []
    counts = []
    
    current_date = twelve_months_ago
    while current_date <= today:
        month_key = current_date.strftime("%Y-%m")
        months.append(month_key)
        counts.append(months_data.get(month_key, 0))
        current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
    
    registration_trend = {
        "months": months,
        "counts": counts
    }

    # 3. 用户行为分析
    review_count = await request.app.mongodb["movies"].aggregate([
        {"$unwind": "$reviews"},
        {"$count": "total"}
    ]).to_list(length=None)
    
    user_count = await request.app.mongodb["users"].count_documents({})
    favorite_count = await request.app.mongodb["users"].count_documents({"favorites": {"$exists": True, "$ne": []}})
    
    user_behaviors = {
        "reviews": review_count[0]["total"] if review_count else 0,
        "favorites": favorite_count,
        "totalUsers": user_count
    }

    return {
        "activityData": activity_data,
        "registrationTrend": registration_trend,
        "userBehaviors": user_behaviors
    } 