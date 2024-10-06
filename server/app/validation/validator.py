from pydantic import BaseModel, Field, field_validator
from app.error.error import *

class OriginalURL(BaseModel):
  original_url: str = Field(..., max_length=2048)

class ShortURL(BaseModel):
  # pydantic 的 Field 字段 error_type: ValueError
  short_url: str = Field(..., pattern=r'^[a-zA-Z0-9]+$')

  @field_validator('short_url')
  def validate_short_url(cls, v: str) -> str:
    if len(v) > 11 or len(v) < 11:
      raise CustomError(name="Validation Error", message="Length does not meet 11 characters.")
    return v
