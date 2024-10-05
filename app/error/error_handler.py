from fastapi import Request
from fastapi.responses import JSONResponse
from app.error.error import *

async def custom_error_handler(req: Request, exc: CustomError):
  return JSONResponse(
    status_code=400,
    content={
      "error_type": exc.name,
      "detail": exc.message,
    }
  )

async def server_interal_error_handler(req: Request, exc: ServerInternalError):
  return JSONResponse(
    status_code=500,
    content={
      "error_type": exc.name,
      "detail": exc.message,
    }
  )