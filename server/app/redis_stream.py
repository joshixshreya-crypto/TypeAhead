
import os
import redis
from dotenv import load_dotenv
from redis_client import redis_client  

load_dotenv()

name = os.getenv("STREAM_NAME")
group_name = os.getenv("GROUP_NAME")

def create_consumer_group():
    print("consumer grouppppp" , name  , group_name)
    # name = os.getenv("STREAM_NAME")
    # group_name = os.getenv("GROUP_NAME")

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
        print(f"Successfully created consumer group '{group_name}' for stream '{name}'")
    except redis.ResponseError as e:
        if "BUSYGROUP" in str(e):
            print(f"Consumer group '{group_name}' already exists for stream '{name}'")
        else:
            print(f"Error creating consumer group: {e}")
            raise 

def create_notification_consumer_group():
    notification_stream= os.getenv("NOTIFICATION_STREAM_NAME")
    notification_consumer = os.getenv("NOTIFICATION_CONSUMER_GROUP_NAME")

    print("Creating notification group , stream name -" , notification_stream)
    if(not notification_stream or not notification_consumer):
        raise RuntimeError("notification stream name or group name is not assigned")
    try:
        redis_client.xgroup_create(
            name = notification_stream,
            groupname=notification_consumer,
            id="0",
            mkstream=True
        )
    except redis.ResponseError as e:
        if "BUSYGROUP" in str(e):
                print(f"{notification_consumer} already exists for stream {notification_stream}")
        else:
                raise RuntimeError(f"Error creating notification consumer group:{notification_consumer}") 
