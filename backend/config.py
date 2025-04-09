from inspect import CO_ASYNC_GENERATOR
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DB_NAME = os.getenv("DB_NAME") 
COLLECTION_NAME = os.getenv("COLLECTION_NAME") 