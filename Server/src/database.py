# database.py
import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = "clinic_db"
COLLECTION_NAME = "appointments"

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

def get_collection(collection_name: str):
    return db[collection_name]