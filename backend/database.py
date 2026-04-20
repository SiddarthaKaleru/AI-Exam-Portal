"""MongoDB async connection via motor."""

from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME

client: AsyncIOMotorClient = None
db = None


async def connect_db():
    """Connect to MongoDB."""
    global client, db
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    print(f"✅ Connected to MongoDB: {DB_NAME}")


async def close_db():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        print("🔌 MongoDB connection closed")


def get_database():
    """Get the database instance."""
    return db
