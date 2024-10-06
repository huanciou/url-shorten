from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi_limiter.depends import RateLimiter
from fastapi.responses import RedirectResponse
from app.const import RATE_LIMITER_SECONDS as seconds, RATE_LIMITER_TIMES as times
from app.validation.validator import *
from app.worker.hash import hash_url
from datetime import datetime, timedelta
from app.const import *

url = APIRouter()

### get redis
async def get_redis(request: Request):
    return request.app.state.redis

### get bf
async def get_bloom_filter(request: Request):
    return request.app.state.bf


### GET method
@url.get("/{url}", dependencies=[Depends(RateLimiter(times=times, seconds=seconds))],
               tags=["Redirection"],
               summary="Redirect Shortened URL to Original URL",
               description="根據用戶提供的短網址，查詢對應的原始 URL，並進行自動跳轉。系統會針對每次請求進行速率限制，以防止濫用行為。")
async def get_url(url: str, 
                  redis = Depends(get_redis), 
                  bf = Depends(get_bloom_filter)):

    try:
        # Validation
        validated_url = ShortURL(short_url=url)
    except ValueError:
        raise CustomError(name="Validation Error", message="Only accepts a-zA-Z characters")
    
    # BF Check
    if url in bf:
        print("MIGHT IN BF, GO ON")

    if not url in bf:  
        print("NOT IN BF")
        return {
            "short_url": url,
            "success": False,
            "reason": "URL Not Exists",
        }
    
    try: 
        # LFU GET
        original_url = await redis.get(url)

        if original_url:
            expiration_date = datetime.now() + timedelta(days=30)
            await redis.expireat(url, expiration_date)
            return RedirectResponse(url=original_url, status_code=307)
        
        return {
            "short_url": url,
            "success": False,
            "reason": "URL Not Exists",
        }
    
    except Exception as e:
        raise ServerInternalError(name="Server Internal Error", message=f"Error retrieving short URL: {e}")

### POST method
@url.post("/", dependencies=[Depends(RateLimiter(times=100, seconds=60))],
                tags=["Create Short URL"],
                summary="Create a Shortened URL for the Given Long URL",
                description="此路由負責將用戶提交的長網址轉換為短網址。每分鐘最多允許 100 次請求，以防止過度創建短網址。")
async def read_url(original_url: OriginalURL, 
                   redis = Depends(get_redis),
                   bf = Depends(get_bloom_filter),
                ):

    try:
        url = original_url.original_url
        short_url = hash_url(url)
    
    except ValueError:
        raise CustomError(name="Validation Error", message="The length exceeds 2048 characters")
    
    try:
        if short_url in bf:
            print("might in BF, go on")
            existing_long_url = await redis.get(short_url)
            if existing_long_url:
                print("url exists")
                expiration_date = datetime.now() + timedelta(days=30)
                await redis.expireat(short_url, expiration_date)
                return {
                    "original_url": existing_long_url,
                    "short_url": DOMAIN_NAME + short_url,
                    "expiration_date": expiration_date,
                    "success": False,
                    "reason": "Short URL Already Exists",
                }

        await redis.set(short_url, original_url.original_url, ex=30*24*60*60) 
        expiration_date = datetime.now() + timedelta(days=30)

        bf.add(short_url)
        
        return {
            "original_url": original_url.original_url,
            "short_url": DOMAIN_NAME + short_url,
            "expiration_date": expiration_date,
            "success": True,
        }
    
    except Exception as e:
        raise ServerInternalError(name="Server Internal Error", message=f"Error storing short URL: {e}")
    