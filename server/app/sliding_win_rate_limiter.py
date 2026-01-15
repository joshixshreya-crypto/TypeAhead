import os
import time
import uuid
from redis_client import redis_client
def sliding_window_rate_limiter(user_id):
    window_size = int(os.getenv('WINDOW_SIZE'))
    max_requests = int(os.getenv('MAX_REQUESTS'))
    now = int(time.time())
    key = f'rl:sw:{user_id}'
    old_timestamp = now - window_size

    # delete older timestamps
    redis_client.zremrangebyscore(key  , 0 , old_timestamp)

    # count the items present in the zset for the key
    request_count = redis_client.zcard(key)

    if(request_count> max_requests):
        return False

    redis_client.zadd(key , {str(now):now})
    return True

