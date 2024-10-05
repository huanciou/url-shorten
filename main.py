from fastapi import FastAPI
import uvicorn
from app.url.urls import url
from typing import Optional
from app.combined_lifespan.combined_lifespan import get_combined_lifespan
from app.error.error import *
from app.error.error_handler import *

# Lifespan
app = FastAPI(lifespan=get_combined_lifespan())

# Error Handler 
app.add_exception_handler(CustomError, custom_error_handler)
app.add_exception_handler(ServerInternalError, server_interal_error_handler)

# Routes
app.include_router(url, prefix="/url_shorten")

@app.get("/set")
async def set_value():
    redis = app.state.redis
    lua_script_sha = app.state.lua_script_sha
    result = await redis.evalsha(lua_script_sha, 0, 'set', "a", 1)
    return {"result": result}

@app.get("/error")
async def make_error():
    try:
        raise ValueError("This is a deliberate ValueError")
    except Exception as e :
        raise CustomError(name="error", message="validation error")

if __name__ == '__main__':
    print("Starting server on port: 3000 ...")
    uvicorn.run("main:app", port=3000, reload=True)