from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as aioredis
from .config import MONGO_URI, DB_NAME, REDIS_HOST, REDIS_PORT

mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DB_NAME]

redis_client = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
