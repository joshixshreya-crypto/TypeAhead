from redis_client import redis_client
from redis_stream import create_notification_consumer_group
import os
from dotenv import load_dotenv
from models.connection_model import NotificationModel
load_dotenv()
import asyncio
import uuid
from database import SessionLocal

async def notification_worker():
    print("Starting notification worker...")
    notification_stream = os.getenv("NOTIFICATION_STREAM_NAME")
    notification_consumer = os.getenv("NOTIFICATION_CONSUMER_GROUP_NAME")

    while True:
        entry = await asyncio.to_thread(redis_client.xreadgroup,
            notification_consumer,
            "notification_worker_1",
            {notification_stream: '>'},
            1,
            5000
        )
        if not entry:
            continue       
        for stream_name , messages in entry:
            for message_id , message_data in messages:
                try:
                    print(f"Processing notification message ID {message_id}")

                    #Creating notification payload
                    notification_payload = {
                        "id" :str(uuid.uuid4()),
                        "user_id" : message_data.get('user_id'),
                        "initiator_id" : message_data.get('initiator_id'),
                        "request_id" : message_data.get('request_id'),
                        "initiator_username": message_data.get('initiator_username'),
                        "notification_type" : "FRIEND_REQUEST",
                        "created_at" : message_data.get('created_at')
                    }
                    
                    #inserting it in notification db
                    await asyncio.to_thread(save_notifications_to_db , notification_payload)
                    
                    redis_client.xack(notification_stream , notification_consumer , message_id)
                except Exception as e:
                    print(f"error processing notification {e} with notification id : {message_id}")
                    continue


def save_notifications_to_db(notification_payload):
    db = SessionLocal()
    try: 
        notification = NotificationModel(
        **notification_payload
        )
        db.add(notification)
        db.commit()
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()
    print(f"Notification created for user {notification_payload.get('user_id')}")

