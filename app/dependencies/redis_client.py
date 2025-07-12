from redis.asyncio import Redis

from app.core.config import get_settings

def get_redis():
    settings = get_settings()
    return Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True, socket_timeout=3, ssl=True)