from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.redis.redis import redis_lifespan
from app.rate_limiter.rate_limiter import rate_limiter_lifespan

@asynccontextmanager
async def combined_lifespan(app: FastAPI):
    async with redis_lifespan(app):
        async with rate_limiter_lifespan(app):
            yield

def get_combined_lifespan():
  return combined_lifespan