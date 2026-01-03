import os
from redis_client import redis_client
from database import SessionLocal
from models.chat_model import roomSchema



async def message_worker():
    GROUP = os.getenv("STREAM_NAME")
    CONSUMER = os.getenv("CONSUMER_NAME")
    STREAM = os.getenv("STREAM_NAME")
    db = SessionLocal()
    try:
        while True:
            # message = await queue.get()
            message = redis_client.xreadgroup(
                groupname=GROUP,
                consumername= CONSUMER,
                streams= {STREAM: '>' },
                count= 1,
                block= 5000

            )
            print("MESSAGES++++++========>" , message)
            sender_id  = message['sender_id']
            msg = message['message']
            room_name = message['room_name']

            # get id via room name
            room  = db.query( roomSchema).filter(roomSchema.room_name == room_name).first()

            room_id = room.id

            # adding message data to db from queue
            # new_record = messageSchema(
            #     id=str(uuid.uuid4()),
            #     room_id =  room_id,
            #     message = msg,   
            #     sender_id = sender_id
            # )
            # db.add(new_record)
            # db.commit()
            # redis_client.xack(
            #     name=STREAM,
            #     groupname=GROUP,
                
                
            # )
    finally:
        db.close()
