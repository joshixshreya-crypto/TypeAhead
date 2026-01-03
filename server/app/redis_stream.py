
import os
import redis
from dotenv import load_dotenv
from redis_client import redis_client  

load_dotenv()

name = os.getenv("STREAM_NAME")
group_name = os.getenv("GROUP_NAME")
print("stream name" , name)
print("group name" , group_name)

def create_consumer_group():
    name = os.getenv("STREAM_NAME")
    group_name = os.getenv("GROUP_NAME")

    print("Creating consumer group - stream name:", name)
    print("Creating consumer group - group name:", group_name)
    if not name or not group_name:
        raise RuntimeError("stream name or group name is not assigned")
    try:
        redis_client.xgroup_create(
          name = name,
          groupname= group_name,
          id = "0",
          mkstream=True
        )
        print(f"✅ Successfully created consumer group '{group_name}' for stream '{name}'")
    except redis.ResponseError as e:
        if "BUSYGROUP" in str(e):
            print(f"ℹ️  Consumer group '{group_name}' already exists for stream '{name}'")
        else:
            print(f"❌ Error creating consumer group: {e}")
            raise 
