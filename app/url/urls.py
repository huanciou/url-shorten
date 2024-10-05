from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from app.const import RATE_LIMITER_SECONDS as seconds, RATE_LIMITER_TIMES as times
from app.validation.validator import *
from app.worker.hash import hash_url

url = APIRouter()

@url.get("/{url}", dependencies=[Depends(RateLimiter(times=times, seconds=seconds))],
              tags=["URL Redirection"],
              summary= "this is a summary", 
              description= "this is a description")
async def get_url(url: str):
    ''' 
    1 判斷短網址有沒有在 redis 當中
    1.1 存在: 直接導向長網址
    1.2 不存在: 跟 DB 拿
    2 更新 Redis 的 LFU
    '''

    try:
        validated_url = ShortURL(short_url=url)
    except ValueError:
        raise CustomError(name="Validation Error", message="Only accepts a-zA-Z characters")

    return {
        "status": 307
    }

@url.post("/", dependencies=[Depends(RateLimiter(times=100, seconds=60))],
               tags=["Shorten URL"],
               summary= "this is a summary", 
               description= "this is a description")
async def read_url():
    
    ''' 
    1 worker() -> 短網址
    2 短網址套入 Bloom Filter
    2.1 !exists -> 回傳結果 + 存入快取
    2.2 exists -> 
    '''

    url = "bc"

    try:
        validated_url = OriginalURL(original_url=url)
        short_url = hash_url(url)
        
    except ValueError:
        raise CustomError(name="Validation Error", message="The length exceeds 2048 characters")
     
    return {
        "original_url:": url,
        "short_url:": short_url,
        "expiration_date:": url,
        "success:": url,
        "reason:": url,
    }