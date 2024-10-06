from fastapi import FastAPI, HTTPException
import uvicorn
from app.url.urls import url
from app.combined_lifespan.combined_lifespan import get_combined_lifespan
from app.error.error import *
from app.error.error_handler import *
from typing import List, Dict, Union

# Lifespan
app = FastAPI(lifespan=get_combined_lifespan())

# Error Handler 
app.add_exception_handler(CustomError, custom_error_handler)
app.add_exception_handler(ServerInternalError, server_interal_error_handler)

# Routes
app.include_router(url, prefix="/url_shorten")

# @app.get("/set")
# async def set_value():
#     redis = app.state.redis
#     lua_script_sha = app.state.lua_script_sha
#     result = await redis.evalsha(lua_script_sha, 0, 'set', "a", 1)
#     return {"result": result}

@app.get("/check", 
         response_model=List[Dict[str, Union[str, int]]])
async def redis_check():
    redis = app.state.redis
    frequency_data = []

    try:
        keys = await redis.keys("*")
        
        for key in keys:
            lfu_counter = await redis.execute_command('OBJECT', 'FREQ', key)
            
            if lfu_counter is not None:
                frequency_info = {
                    "key": key,
                    "lfu_counter": lfu_counter,
                }
                frequency_data.append(frequency_info)
    
        return frequency_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving frequency data: {e}")

if __name__ == '__main__':
    print("Starting server on port: 3000 ...")
    uvicorn.run("main:app", port=3000, reload=True)