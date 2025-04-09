from pydantic import BaseModel
from typing import List, Optional

class Review(BaseModel):
    review_id: str
    uname: str
    gender: str
    profileUrl: str
    content: str

class Image(BaseModel):
    type: str
    content: str

class Movie(BaseModel):
    movie_id: str
    title: str
    genre: str
    description: str
    url_film: str
    img: Image
    source: str

class MovieDetail(Movie):
    reviews: List[Review]