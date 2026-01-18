import os
from redis_client import redis_client
import time
def rate_limiter(userid):
    window_size = int(os.getenv('WINDOW_SIZE'))
    max_requests = int(os.getenv('MAX_REQUESTS'))
    current_time = int(time.time())
    window_id  = current_time//window_size
    redis_key = f"rate:{userid}:{window_id}"
    count = redis_client.incr(redis_key)
    
    if(count == 1):
        redis_client.expire(redis_key, window_size)
    
    if(count > max_requests):
        return False
    return True



