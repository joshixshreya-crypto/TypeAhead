
import os
import redis
from redis_client import redis_client  

name = os.getenv("STREAM_NAME")
group_name = os.getenv("GROUP_NAME")
print("stream name" , name)
print("group name" , group_name)

def create_consumer_group():
    name = os.getenv("STREAM_NAME")
    group_name = os.getenv("GROUP_NAME")

    print("stream name" , name)
    print("group name" , group_name)
    if not name or not group_name:
        raise RuntimeError("stream name or group name is not assigned")
    try:
        redis_client.xgroup_create(
          name = name,
          groupname= group_name,
          id = "0",
          mkstream=True
        )
    except redis.ResponseError as e:
        if "BUSYGROUP" in str(e):
            print("stream already exists" , e)
        else:
            raise 
