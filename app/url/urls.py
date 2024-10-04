from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from app.const import RATE_LIMITER_SECONDS as seconds, RATE_LIMITER_TIMES as times

url = APIRouter()

@url.get("/", dependencies=[Depends(RateLimiter(times=times, seconds=seconds))],
              tags=["URL Redirection"],
              summary= "this is a summary", 
              description= "this is a description")
async def get_url(url: str = "hihi"):
    ''' 
    1 判斷短網址有沒有在 redis 當中
    1.1 存在: 直接導向長網址
    1.2 不存在: 跟 DB 拿
    2 更新 Redis 的 LFU
    '''

    return {
        "status": 307
    }

@url.post("/", dependencies=[Depends(RateLimiter(times=5, seconds=60))],
               tags=["Shorten URL"],
               summary= "this is a summary", 
               description= "this is a description")
async def read_url(url: str = "hihi"):
    
    ''' 
    1 worker() -> 短網址
    2 短網址套入 Bloom Filter
    2.1 !exists -> 回傳結果 + 存入快取
    2.2 exists -> 
    '''
     
    return {
        "original_url:": url,
        "short_url:": url,
        "expiration_date:": url,
        "success:": url,
        "reason:": url,
    }