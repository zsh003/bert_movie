from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from routers import movies, analysis, users, reviews, favorites
from routers.users import login
import config
from database.database import connect_to_mongo, close_mongo_connection

app = FastAPI(title="Movie Analysis System API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(config.MONGODB_URL)
    app.mongodb = app.mongodb_client[config.DB_NAME]
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()
    await close_mongo_connection()

# 包含路由
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.add_api_route("/token", login, methods=["POST"], tags=["auth"]) # 注册两个token节点
app.include_router(movies.router, prefix="/api/movies", tags=["movies"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["favorites"])

@app.get("/")
async def root():
    return {"message": "Welcome to Movie Review Sentiment Analysis API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 