import os
import time
from redis_client import redis_client

def token_bucket_rl(user_id):
    token_ps = float(os.getenv('TOKEN_PER_SECOND'))  
    max_token = int(os.getenv('MAX_TOKENS'))    
    now = int(time.time())
    key = f'rl:tb:{user_id}'

    token_left = redis_client.hget(key , 'tokens')  
    last_refill_time = redis_client.hget(key , 'time')

    token_left  = int(token_left)  if token_left is not None else max_token
    last_refill_time = int(last_refill_time) if last_refill_time is not None else now

    time_elapsed = now - last_refill_time

    refill_token_val = min(max_token  , token_left + token_ps * time_elapsed) 
    
    if(refill_token_val < 1):
        return False

    refill_token_val = refill_token_val-1
    redis_client.hset(name =key , mapping={'tokens': refill_token_val , 'time': now})


    redis_client.expire(key , max_token*3)
    return True


    

