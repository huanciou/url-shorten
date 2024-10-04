from fastapi import FastAPI
import uvicorn
from app.url.urls import url
from typing import Optional
from pydantic import BaseModel, Field, ValidationError
from app.combined_lifespan.combined_lifespan import get_combined_lifespan

app = FastAPI(lifespan=get_combined_lifespan())

app.include_router(url, prefix="/url")

@app.get("/set")
async def set_value():
    redis = app.state.redis
    lua_script_sha = app.state.lua_script_sha
    result = await redis.evalsha(lua_script_sha, 0, 'set', "a", 1)
    return {"result": result}

if __name__ == '__main__':
    print("Starting server on port: 3000 ...")
    uvicorn.run("main:app", port=3000, reload=True)