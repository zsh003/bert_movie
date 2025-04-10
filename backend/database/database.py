from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGODB_URL, DB_NAME

client = None
db = None

async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
async def close_mongo_connection():
    global client
    if client is not None:
        client.close()

def get_database():
    return db 