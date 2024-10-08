from typing import AsyncIterator
from redis.asyncio import Redis
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.const import *
from pybloom_live import BloomFilter
import os

async def init_redis_pool() -> Redis:
    redis = Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
    
    try:
        await redis.ping()
        print("Redis Connection Successful")
        maxmemory_policy = await redis.config_set("maxmemory-policy", "volatile-lfu")
        maxmemory = await redis.config_set("maxmemory", "100mb")

        print(f"Volatile-lfu Policy Status: {maxmemory_policy}")
        print(f"Maxmemory Setup: {maxmemory}")
        
    except Exception as e:
        print(f"Redis Connection Failed: {e}")
        raise
    
    return redis

@asynccontextmanager
async def redis_lifespan(app: FastAPI):
    try:
        redis = await init_redis_pool()
        app.state.redis = redis

        # preload BF
        bloom_filter = BloomFilter(capacity=100000, error_rate=0.01)
        app.state.bf = bloom_filter

        await initialize_bloom_filter(redis, bloom_filter)
        
        # preload LUA 
        app.state.lua_script_sha = await load_lua_script(redis)
        
        yield
    finally:
        await app.state.redis.close()
        print("Redis Connection Close")

async def load_lua_script(redis: Redis) -> str:
    script_path = os.path.join(os.path.dirname(__file__), 'set.lua')
    with open(script_path, 'r') as file:
        lua_script = file.read()
    return await redis.script_load(lua_script)

async def initialize_bloom_filter(redis: Redis, bloom_filter: BloomFilter):
    keys = await redis.keys("*")
    
    for key in keys:
        if not key.startswith("fastapi-limiter"):
            bloom_filter.add(key)
    print("Bloom Filter Initialized Successfully")