from fastapi import APIRouter, Request, HTTPException
from typing import List
from models.movie import Movie, MovieDetail
from bson import ObjectId

router = APIRouter()

@router.get("/", response_model=List[Movie])
async def get_movies(request: Request, skip: int = 0, limit: int = 10):
    movies = await request.app.mongodb["movies"].find().skip(skip).limit(limit).to_list(length=limit)
    return movies

@router.get("/{movie_id}", response_model=MovieDetail)
async def get_movie(movie_id: str, request: Request):
    movie = await request.app.mongodb["movies"].find_one({"movie_id": {"$numberLong": movie_id}})
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@router.get("/genres/stats")
async def get_genre_stats(request: Request):
    pipeline = [
        {"$unwind": "$genre"},
        {"$group": {"_id": "$genre", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    genres = await request.app.mongodb["movies"].aggregate(pipeline).to_list(length=None)
    return genres 