import os

# Get Redis connection details from environment variables
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')  # Default to 'localhost' if not set
REDIS_PORT = os.getenv('REDIS_PORT', 6379)          # Default to 6379 if not set

# Use these variables to create your Redis client
import redis

def get_redis_client():
    redis_client = redis.StrictRedis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=0,
        decode_responses=True
    )
    return redis_client
