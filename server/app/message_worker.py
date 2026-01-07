import os
import uuid
from dotenv import load_dotenv
from redis_client import redis_client
from database import SessionLocal
from models.chat_model import roomSchema, messageSchema

load_dotenv()

async def message_worker():
    print("++++++++++++++++++++++++++++++++++++++message worker started++++++++++++++++++++++++++++++++++++++++++++")
    GROUP = os.getenv("GROUP_NAME")
    CONSUMER = os.getenv("CONSUMER_NAME")
    STREAM = os.getenv("STREAM_NAME")
    db = SessionLocal()
    try:
        while True:
            # Read messages from Redis stream
            messages = redis_client.xreadgroup(
                groupname=GROUP,
                consumername=CONSUMER,
                streams={STREAM: '>'},
                count=1,
                block=5000
            )
            
            # Check if we got any messages
            if not messages:
                continue
                
            # Parse the Redis stream response
            # Format: [[stream_name, [(message_id, {field: value, ...})]]]
            for stream_name, message_list in messages:
                for message_id, message_data in message_list:
                    print(f"Processing message {message_id}: {message_data}")
                    
                    sender_id = message_data.get('sender_id')
                    msg = message_data.get('message')
                    room_name = message_data.get('room_name')
                    
                    if not sender_id or not msg or not room_name:
                        print(f"Invalid message data: {message_data}")
                        # Acknowledge the message even if invalid
                        redis_client.xack(STREAM, GROUP, message_id)
                        continue

                    # Get room id via room name
                    room = db.query(roomSchema).filter(roomSchema.room_name == room_name).first()
                    
                    if not room:
                        print(f"Room '{room_name}' not found")
                        redis_client.xack(STREAM, GROUP, message_id)
                        continue
                    
                    room_id = room.id

                    # Adding message data to db from queue
                    print("===============================>+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++>Room id , message , sender id" , room_id , msg , sender_id)
                    new_record = messageSchema(
                        id=str(uuid.uuid4()),
                        room_id=room_id,
                        message=msg,   
                        sender_id=sender_id
                    )
                    db.add(new_record)
                    db.commit()
                    
                    # Acknowledge message processing
                    redis_client.xack(STREAM, GROUP, message_id)
                    print(f" Message saved to DB and acknowledged: {message_id}")
                    
    except Exception as e:
        print(f"Error in message_worker: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
