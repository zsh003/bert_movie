from fastapi import APIRouter, Request, HTTPException
from typing import List
from models.movie import Movie, MovieDetail
from bson import ObjectId

router = APIRouter()

@router.get("/", response_model=List[Movie])
async def get_movies(request: Request, skip: int = 0, limit: int = 1):
    pipeline = [
        {"$project": {
            "_id": 0,
            "movie_id": 1,
            "title": 1,
            "genre": 1,
            "description": 1,
            "url_film": 1,
            "img": 1,
            "source": 1 
        }},
        {"$skip": skip},
        {"$limit": limit}
    ]
    movies = await request.app.mongodb["movies"].aggregate(pipeline).to_list(length=limit)
    return movies

@router.get("/{movie_id}", response_model=MovieDetail)
async def get_movie(movie_id: int, request: Request):
    movie = await request.app.mongodb["movies"].find_one({
        "movie_id": movie_id
    })
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    # # 转换_id字段为字符串（BSON ObjectId需要序列化）
    # if '_id' in movie:
    #     movie['_id'] = str(movie['_id'])
    return movie

@router.get("/genres/stats")
async def get_genre_stats(request: Request):
    pipeline = [
        {"$addFields": {"genre": {"$split": ["$genre", ";"]}}},
        {"$unwind": "$genre"},
        {"$group": {"_id": "$genre", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    genres = await request.app.mongodb["movies"].aggregate(pipeline).to_list(length=None)
    return genres 