from fastapi import FastAPI, Depends
from fastapi_limiter import FastAPILimiter
from contextlib import asynccontextmanager

@asynccontextmanager
async def rate_limiter_lifespan(app: FastAPI):
    try:
        redis_connection = app.state.redis
        await FastAPILimiter.init(redis_connection)
        yield
    finally:
        await FastAPILimiter.close()