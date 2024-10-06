from fnvhash import fnv1a_64
import base62

def hash_url(url: str) -> str:
  url_bytes = url.encode('utf-8')

  hash_bytes = fnv1a_64(url_bytes)

  base62_str = base62.encode(hash_bytes) # Base62 encode 不會以 0 開頭

  return base62_str.zfill(11) # 從 '最左側' 補 0, 不會與現有產生 collison 


